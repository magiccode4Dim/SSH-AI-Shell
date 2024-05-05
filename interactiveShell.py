from .ShellHandler import ShellHandler




sh = ShellHandler("localhost","nany","2001")
r = sh.execute("ifconfig")
output= r[1]
print("".join(output))