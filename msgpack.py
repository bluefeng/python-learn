
import msgpack
import sys
# import traceback

def pack(info):
	info = eval(info)
	ret = msgpack.packb(info, use_bin_type = True) #打包
	print('"' +  str(ret)[2:-1] + '"')
def unpack(info):
	info = eval('b\"' + info + '\"') #去除转义字符
	ret = msgpack.unpackb(info, raw = False) #解包
	print('"' + str(ret) + '"')

if __name__ == "__main__":
	try:
		cmd = sys.argv[1]
		info = sys.argv[2]
		if cmd == "pack" : 
			pack(info)
		elif cmd == "unpack" :
			unpack(info)
		else:
			raise
	except:
		# traceback.print_exc()
		print("cmds:  pack   unpack  \nneed info")
