# Compile the framebuddy

1. Check out the micropython repository. Right here in the source dir works great
```
git clone https://github.com/micropython/micropython.git
```
2. Install pyelftools
```
pip3 install --user pyelftools
```
3. Make sure you've got a cross-compiler for armv6m
```
sudo apt install gcc-arm-none-eabi
```
4. Build the module
```
make
```
5. Include framebuddy.mpy in the same directory as `fb.py` when you deploy to your board