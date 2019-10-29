# Git Hot Reload
Lightweight server written in python using starlette for listening to githhub web hooks.

### Usage
- - - -
#### Mac OS
1. brew install git
2. brew install git-lfs
3. git clone https://github.com/seanaye/git_hotreload.git
4. brew install python3
5. cd git_hotreload
6. python3 -m venv env
7. source env_bin_activate
8. pip install -r requirements.txt
9. Create a variable ‘key’ in secretkey.py
10. uvicorn app:app —host 0.0.0.0 —port 4567
- - - -
#### Ubuntu
1. sudo apt-get install git
2. sudo apt-get install git-lfs
3. git clone https://github.com/seanaye/git_hotreload.git
4. sudo apt-get install python3
5. cd git_hotreload
6. python3 -m venv env
7. source env_bin_activate
8. pip install -r requirements.txt
9. Create a variable ‘key’ in secretkey.py
10. uvicorn app:app —host 0.0.0.0 —port 4567
- - - -
11. Set repository webhook to server and port in Github
12. Optionally configure docker-compose.yml in home directory