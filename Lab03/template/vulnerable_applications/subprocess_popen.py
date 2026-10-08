import subprocess

def popen1(user):
    subprocess.Popen("echo " + user)

def popen2(user):
    subprocess.Popen("echo " + user, shell=True)

def popen3(user):
    subprocess.run(["sh", "-c", "echo " + user])

def popen4(user):
    subprocess.run(["sh", "-c", "echo " + user], shell=True)

def popen5(user):
    subprocess.Popen("echo hello", shell=True)

def popen6():
    subprocess.run(["echo", "hello"], shell=True)

def popen7(user):
    subprocess.run(args=user, shell=True)

def popen8(user):
    subprocess.run(user, shell=True, check=True)

def popen9():
    subprocess.run("echo hello", shell=True, check=True)

def popen10():
    subprocess.run(args=["echo", "hello"], shell=True)

def popen11(user):
    subprocess.run(args=["sh", "-c", "echo " + user], shell=True)