import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import paramiko
import json
import os
import subprocess
import base64

class SSHConnectionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SSH连接管理器")
        self.root.geometry("500x400")
        
        # 配置文件路径
        self.config_file = "ssh_configs.json"
        self.configs = self.load_configs()
        
        # 创建界面组件
        self.create_widgets()
        
        # 加载配置到下拉菜单
        self.load_configs_to_dropdown()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # IP地址输入
        ttk.Label(main_frame, text="IP地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(main_frame, width=30)
        self.ip_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 用户名输入
        ttk.Label(main_frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 端口号输入
        ttk.Label(main_frame, text="端口号:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.port_entry.insert(0, "22")  # 默认端口
        
        # 密码输入
        ttk.Label(main_frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 配置选择下拉菜单
        ttk.Label(main_frame, text="选择配置:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.config_var = tk.StringVar()
        self.config_dropdown = ttk.Combobox(main_frame, textvariable=self.config_var, width=27, state="readonly")
        self.config_dropdown.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.config_dropdown.bind("<<ComboboxSelected>>", self.on_config_selected)
        
        # 连接按钮
        self.connect_btn = ttk.Button(main_frame, text="连接", command=self.connect_ssh)
        self.connect_btn.grid(row=4, column=2, padx=(5, 0), pady=5)
        
        # 操作按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        # 保存配置按钮
        self.save_btn = ttk.Button(button_frame, text="保存配置", command=self.save_config)
        self.save_btn.grid(row=0, column=0, padx=5)
        
        # 删除配置按钮
        self.delete_btn = ttk.Button(button_frame, text="删除配置", command=self.delete_config)
        self.delete_btn.grid(row=0, column=1, padx=5)
        
        # 重命名配置按钮
        self.rename_btn = ttk.Button(button_frame, text="重命名配置", command=self.rename_config)
        self.rename_btn.grid(row=0, column=2, padx=5)
        
        # 信息显示区域
        self.info_text = tk.Text(main_frame, height=15, width=60)
        self.info_text.grid(row=6, column=0, columnspan=3, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.info_text.yview)
        scrollbar.grid(row=6, column=3, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # 配置列权重
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def load_configs(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {e}")
                return {}
        return {}
    
    def save_configs_to_file(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件失败: {e}")
    
    def load_configs_to_dropdown(self):
        """加载配置到下拉菜单"""
        config_names = list(self.configs.keys())
        self.config_dropdown['values'] = config_names
        if config_names:
            self.config_dropdown.current(0)
            # 自动填充第一个配置的信息
            self.fill_config_fields(config_names[0])
    
    def fill_config_fields(self, config_name):
        """填充配置字段"""
        if config_name in self.configs:
            config = self.configs[config_name]
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, config['ip'])
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, config['username'])
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(config['port']))
            self.password_entry.delete(0, tk.END)
            # 解码密码
            if 'password' in config and config['password']:
                try:
                    decoded_pwd = base64.b64decode(config['password']).decode('utf-8')
                    self.password_entry.insert(0, decoded_pwd)
                except:
                    pass
    
    def on_config_selected(self, event):
        """配置选择事件"""
        selected_config = self.config_var.get()
        self.fill_config_fields(selected_config)
    
    def save_config(self):
        """保存当前配置"""
        ip = self.ip_entry.get().strip()
        username = self.username_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not ip or not username or not port:
            messagebox.showwarning("警告", "请填写完整的配置信息")
            return
        
        # 验证端口是否为数字
        try:
            port_num = int(port)
            if port_num <= 0 or port_num > 65535:
                raise ValueError("端口号必须在1-65535之间")
        except ValueError:
            messagebox.showerror("错误", "端口号必须是1-65535之间的数字")
            return
        
        # 获取配置名称
        config_name = simpledialog.askstring("保存配置", "请输入配置名称:", 
                                            initialvalue=f"{username}@{ip}")
        if not config_name:
            return
        
        # 保存配置（密码用base64编码保存）
        password = self.password_entry.get()
        encoded_pwd = base64.b64encode(password.encode('utf-8')).decode('utf-8') if password else ''
        self.configs[config_name] = {
            'ip': ip,
            'username': username,
            'port': port_num,
            'password': encoded_pwd
        }
        
        self.save_configs_to_file()
        self.load_configs_to_dropdown()
        
        messagebox.showinfo("成功", f"配置 '{config_name}' 已保存")
    
    def delete_config(self):
        """删除选中的配置"""
        selected_config = self.config_var.get()
        if not selected_config:
            messagebox.showwarning("警告", "请选择要删除的配置")
            return
        
        if messagebox.askyesno("确认", f"确定要删除配置 '{selected_config}' 吗？"):
            del self.configs[selected_config]
            self.save_configs_to_file()
            self.load_configs_to_dropdown()
            self.config_var.set("")
            messagebox.showinfo("成功", f"配置 '{selected_config}' 已删除")
    
    def rename_config(self):
        """重命名选中的配置"""
        selected_config = self.config_var.get()
        if not selected_config:
            messagebox.showwarning("警告", "请选择要重命名的配置")
            return
        
        new_name = simpledialog.askstring("重命名配置", "请输入新的配置名称:", 
                                         initialvalue=selected_config)
        if not new_name:
            return
        
        if new_name in self.configs:
            messagebox.showerror("错误", f"配置名称 '{new_name}' 已存在")
            return
        
        # 重命名配置
        self.configs[new_name] = self.configs.pop(selected_config)
        self.save_configs_to_file()
        self.load_configs_to_dropdown()
        self.config_var.set(new_name)
        messagebox.showinfo("成功", f"配置已重命名为 '{new_name}'")
    
    def connect_ssh(self):
        """连接SSH"""
        ip = self.ip_entry.get().strip()
        username = self.username_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not ip or not username or not port:
            messagebox.showwarning("警告", "请填写完整的连接信息")
            return
        
        try:
            port_num = int(port)
            if port_num <= 0 or port_num > 65535:
                raise ValueError("端口号必须在1-65535之间")
        except ValueError:
            messagebox.showerror("错误", "端口号必须是1-65535之间的数字")
            return
        
        # 清空信息显示区域
        self.info_text.delete(1.0, tk.END)
        
        # 尝试连接
        try:
            self.info_text.insert(tk.END, f"正在连接 {username}@{ip}:{port}...\n")
            self.root.update()
            
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接到SSH服务器
            password = self.password_entry.get()
            ssh.connect(hostname=ip, port=port_num, username=username, password=password, timeout=10)
            
            # 连接成功
            self.info_text.insert(tk.END, "连接成功！\n")
            self.info_text.insert(tk.END, f"已连接到 {username}@{ip}:{port}\n")
            
            # 测试执行命令
            stdin, stdout, stderr = ssh.exec_command('uname -a')
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if output:
                self.info_text.insert(tk.END, f"系统信息: {output}\n")
            
            if error:
                self.info_text.insert(tk.END, f"错误信息: {error}\n")
            
            # 关闭测试连接
            ssh.close()
            
            # 打开终端进行交互式SSH连接
            self.info_text.insert(tk.END, "正在打开终端...\n")
            self.open_ssh_terminal(ip, port_num, username, password)
            
        except Exception as e:
            error_msg = f"连接失败: {str(e)}\n"
            self.info_text.insert(tk.END, error_msg)
            messagebox.showerror("连接失败", error_msg)
    
    def open_ssh_terminal(self, ip, port, username, password):
        """打开终端进行交互式SSH连接"""
        try:
            # 使用Windows Terminal或cmd打开SSH连接
            # 优先尝试使用sshpass（如果安装了），否则使用普通ssh命令
            ssh_cmd = f'ssh -p {port} {username}@{ip}'
            
            # 尝试使用Windows Terminal
            try:
                subprocess.Popen(['wt', 'cmd', '/k', ssh_cmd], shell=True)
                self.info_text.insert(tk.END, "已在Windows Terminal中打开SSH连接\n")
            except:
                # 如果Windows Terminal不可用，使用cmd
                subprocess.Popen(f'start cmd /k {ssh_cmd}', shell=True)
                self.info_text.insert(tk.END, "已在命令提示符中打开SSH连接\n")
            
            self.info_text.insert(tk.END, "请在终端窗口中输入密码进行连接\n")
            
        except Exception as e:
            self.info_text.insert(tk.END, f"打开终端失败: {str(e)}\n")
            messagebox.showerror("错误", f"打开终端失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SSHConnectionManager(root)
    root.mainloop()