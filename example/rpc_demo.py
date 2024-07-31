# client.py
import xmlrpc.client

"""
 telnet 192.168.10.59 61001

 sudo apt-get install nmap

 查看服务器端口是否开放
 nmap -p 61001 192.168.10.59
"""


def main():
    with xmlrpc.client.ServerProxy("http://192.168.10.59:61001/") as proxy:
        script_path = "/mnt/nfs_share_test/yangruiqing/rpc_server/a.py"
        result = proxy.run_script2(script_path)
        # print(f"Script output:\n{result}")


if __name__ == "__main__":
    main()
