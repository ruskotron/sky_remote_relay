
from sky_remote import SkyRemote

r = SkyRemote('192.168.0.66')

def do_read(f):

  while True:

    l = f.readline()
    k = l.strip()

    print(f'{k}')

    if not l:
        break

    try:
        r.press(int(k))
    except:
        r.press(k)


while True:
  with open('my_fifo') as f:
    do_read(f)



print('sky remote server end')
     
