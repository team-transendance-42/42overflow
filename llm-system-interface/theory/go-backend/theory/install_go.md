Move the unzipped go folder to /usr/local (the standard location for Go):

Open your WSL terminal.

Move the folder (replace go1.22.x with your actual folder name):
sudo mv ~/Desktop/go /usr/local

Add Go to your PATH (if not already):
export PATH=$PATH:/usr/local/go/bin

Add that line to your ~/.profile or ~/.bashrc for persistence.

Now you can use Go from anywhere in your WSL terminal. 