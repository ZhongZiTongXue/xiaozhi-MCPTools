"""
此脚本用于连接到MCP服务器，并将输入和输出通过WebSocket端点进行管道传输。
版本：1.6.0-详细连接日志

粽子同学完善注释

用法：
1. 设置环境变量：export MCP_ENDPOINT=<your_mcp_endpoint>
2. 运行脚本：python mcp_pipe.py <your_mcp_script>

"""

import asyncio
import websockets
import subprocess
import logging
import os
import signal
import sys
import random
from dotenv import load_dotenv

# 从环境变量文件加载环境变量
load_dotenv()

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,    # 日志详细程度  DEBUG > INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 获取日志记录器并设置名称
logger = logging.getLogger('MCP_PIPE')

# 重连设置参数
INITIAL_BACKOFF = 1  # 初始等待时间（秒）
MAX_BACKOFF = 60  # 最大等待时间（秒）
reconnect_attempt = 0  # 重连尝试次数
backoff = INITIAL_BACKOFF  # 当前重连等待时间

# 用于存储状态文件路径的变量
status_file_path = r"C:\xiaozhi\MCP\MCP_Windows\数据\成功连接MCP.exe"


async def connect_with_retry(uri):
    """
    连接到WebSocket服务器，带有重连机制
    
    此函数会无限尝试连接到指定的WebSocket服务器地址，
    如果连接失败会按照指数退避算法增加重连间隔时间，
    并添加随机抖动避免重连风暴。
    """
    global reconnect_attempt, backoff
    while True:  # 无限重连循环
        try:
            if reconnect_attempt > 0:
                # 计算等待时间，添加随机抖动（0-10%）
                wait_time = backoff * (1 + random.random() * 0.1)
                logger.info(f"等待 {wait_time:.2f} 秒后进行第 {reconnect_attempt} 次重连尝试...")
                await asyncio.sleep(wait_time)
            
            # 尝试连接到服务器
            await connect_to_server(uri)
        
        except Exception as e:
            # 连接失败，增加重连尝试次数
            reconnect_attempt += 1
            logger.warning(f"连接关闭（尝试次数：{reconnect_attempt}）: {e}")
            # 计算下一次重连的等待时间（指数退避，最大不超过MAX_BACKOFF）
            backoff = min(backoff * 2, MAX_BACKOFF)

async def connect_to_server(uri):
    """
    连接到WebSocket服务器，并与指定的MCP脚本建立双向通信
    
    此函数负责：
    1. 使用WebSocket连接到服务器
    2. 启动本地MCP脚本进程
    3. 创建三个任务：
       a. 将WebSocket数据写入MCP脚本的标准输入
       b. 将MCP脚本的标准输出发送到WebSocket
       c. 将MCP脚本的标准错误输出打印到终端
    """
    global reconnect_attempt, backoff,status_file_path
    try:
        logger.info("正在连接到WebSocket服务器...")
        # 使用上下文管理器连接WebSocket
        async with websockets.connect(uri) as websocket:
            logger.info("成功连接到WebSocket服务器")
            
            # 重置重连参数
            reconnect_attempt = 0
            backoff = INITIAL_BACKOFF
            
            # 启动MCP脚本进程
            process = subprocess.Popen(
                ['python', mcp_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False  # 使用二进制模式（重要：确保数据完整性）
            )
            logger.info(f"已启动 {mcp_script} 进程 (PID: {process.pid})")
            
            # 创建状态文件
            if status_file_path:
                try:
                    with open(status_file_path, 'w') as f:
                        f.write(f"进程已启动：{mcp_script} (PID: {process.pid})")
                    logger.info(f"\n\n\n\t\tMCP服务准备就绪！\n\n")
                except Exception as e:
                    logger.error(f"创建状态文件失败：{e}")


            # 创建三个异步任务并行执行
            await asyncio.gather(
                pipe_websocket_to_process(websocket, process),  # WebSocket到进程
                pipe_process_to_websocket(process, websocket),  # 进程到WebSocket
                pipe_process_stderr_to_terminal(process)  # 进程错误输出到终端
            )
    except websockets.exceptions.ConnectionClosed as e:
        # WebSocket连接关闭异常处理
        logger.error(f"WebSocket连接关闭: {e}")
        raise  # 重新抛出异常触发重连
    except Exception as e:
        # 其他异常处理
        logger.error(f"连接错误: {e}")
        raise  # 重新抛出异常触发重连
    finally:
        # 确保子进程正确终止（即使发生异常）
        if 'process' in locals():
            logger.info(f"正在终止 {mcp_script} 进程 (PID: {process.pid})")
            try:
                # 尝试优雅终止进程
                process.terminate()
                # 等待进程退出，超时5秒
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果超时，则强制杀死进程
                process.kill()
            logger.info(f"{mcp_script} 进程已终止")

            # 删除状态文件
            if status_file_path and os.path.exists(status_file_path):
                try:
                    os.remove(status_file_path)
                    logger.info(f" MCP服务未正常运行")
                except Exception as e:
                    logger.error(f"删除状态文件失败：{e}")



async def pipe_websocket_to_process(websocket, process):
    """
    将WebSocket接收到的数据写入MCP脚本的标准输入
    
    此函数负责：
    1. 从WebSocket接收数据
    2. 将接收到的数据写入MCP脚本的标准输入
    3. 处理可能的异常并记录日志
    """
    try:
        while True:
            # 从WebSocket接收数据（自动处理文本和二进制数据）
            message = await websocket.recv()
            logger.debug(f"从WebSocket收到消息: {message[:120]}...")  # 限制日志长度

            # 确保数据以二进制形式写入
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            # 写入进程标准输入并刷新缓冲区
            process.stdin.write(message + b'\n')
            process.stdin.flush()
    except Exception as e:
        # 捕获异常并记录错误日志
        logger.error(f"WebSocket到进程管道发生错误: {e}")
        raise  # 重新抛出异常触发重连

        # 删除状态文件
        if status_file_path and os.path.exists(status_file_path):
            try:
                os.remove(status_file_path)
                logger.info(f" MCP服务未正常运行")
            except Exception as e:
                logger.error(f"删除状态文件失败：{e}")


    finally:
        # 确保标准输入关闭
        if not process.stdin.closed:
            process.stdin.close()

async def pipe_process_to_websocket(process, websocket):
    """
    将MCP脚本的标准输出发送到WebSocket
    
    此函数负责：
    1. 从MCP脚本的标准输出读取数据
    2. 将读取到的数据发送到WebSocket
    3. 处理可能的异常并记录日志
    """
    try:
        while True:
            # 从进程标准输出读取一行数据（使用异步执行器运行阻塞调用）
            data = await asyncio.get_event_loop().run_in_executor(
                None,  # 使用默认执行器
                process.stdout.readline  # 阻塞调用
            )
            
            if not data:  # 如果没有数据，表示进程可能已结束
                logger.info("进程已结束输出")
                break
                
            # 将二进制数据解码为字符串并发送到WebSocket
            text = data.decode('utf-8')
            
            logger.debug(f"向WebSocket发送消息: {text[:120]}...")  # 限制日志长度
            
            await websocket.send(text)
    except Exception as e:
        logger.error(f"进程到WebSocket管道发生错误: {e}")
        raise  # 重新抛出异常触发重连

        # 删除状态文件
        if status_file_path and os.path.exists(status_file_path):
            try:
                os.remove(status_file_path)
                logger.info(f" MCP服务未正常运行")
            except Exception as e:
                logger.error(f"删除状态文件失败：{e}")


async def pipe_process_stderr_to_terminal(process):
    """
    将MCP脚本的标准错误输出打印到终端
    
    此函数负责：
    1. 从MCP脚本的标准错误读取数据
    2. 将读取到的数据打印到终端
    3. 处理可能的异常并记录日志
    """
    try:
        while True:
            # 从进程标准错误读取一行数据（使用异步执行器运行阻塞调用）
            data = await asyncio.get_event_loop().run_in_executor(
                None,  # 使用默认执行器
                process.stderr.readline  # 阻塞调用
            )
            
            if not data:  # 如果没有数据，表示进程可能已结束
                logger.info("进程已结束标准错误输出")


                # 删除状态文件
                if status_file_path and os.path.exists(status_file_path):
                    try:
                        os.remove(status_file_path)
                        logger.info(f"\n\n\n\t\tMCP服务被终止！！\n\n")
                    except Exception as e:
                        logger.error(f"删除状态文件失败：{e}")


                break


            # 将二进制数据解码为字符串并打印到标准错误输出
            sys.stderr.write(data.decode('utf-8'))
            sys.stderr.flush()  # 立即刷新缓冲区
    except Exception as e:
        logger.error(f"进程标准错误管道发生错误: {e}")
        raise  # 重新抛出异常触发重连

        # 删除状态文件
        if status_file_path and os.path.exists(status_file_path):
            try:
                os.remove(status_file_path)
                logger.info(f" MCP服务未正常运行")
            except Exception as e:
                logger.error(f"删除状态文件失败：{e}")


def signal_handler(sig, frame):
    """
    处理中断信号（如Ctrl+C），优雅地关闭程序
    
    此函数会在收到SIGINT信号时被调用，
    记录日志并退出程序。
    """
    logger.info("收到中断信号，正在关闭...")
    sys.exit(0)

    # 删除状态文件
    if status_file_path and os.path.exists(status_file_path):
        try:
            os.remove(status_file_path)
            logger.info(f" MCP服务未正常运行")
        except Exception as e:
            logger.error(f"删除状态文件失败：{e}")


if __name__ == "__main__":
    # 注册信号处理程序，处理Ctrl+C等中断信号
    signal.signal(signal.SIGINT, signal_handler)
    
    # 检查命令行参数是否正确
    if len(sys.argv) < 2:
        logger.error("用法: mcp_pipe.py <mcp_script>")
        sys.exit(1)
    
    # 获取命令行传入的MCP脚本路径
    mcp_script = sys.argv[1]
    
    # 从环境变量获取MCP服务器地址
    endpoint_url = os.environ.get('MCP_ENDPOINT')
    if not endpoint_url:
        logger.error("请设置 `MCP_ENDPOINT` 环境变量")
        sys.exit(1)
    
    # 启动主异步循环
    try:
        logger.info("启动MCP管道程序...")
        asyncio.run(connect_with_retry(endpoint_url))
    except KeyboardInterrupt:
        # 捕获键盘中断（Ctrl+C）
        logger.info("程序被用户中断")
    except Exception as e:
        # 捕获其他异常
        logger.error(f"程序执行错误: {e}")

                # 删除状态文件
        if status_file_path and os.path.exists(status_file_path):
            try:
                os.remove(status_file_path)
                logger.info(f" MCP服务未正常运行")
            except Exception as e:
                logger.error(f"删除状态文件失败：{e}")