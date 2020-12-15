from PIL import Image
from numpy import asarray
import os

def file_exists(file_path):
	return os.path.isfile(file_path)
def valid_image(file_ext):
	return file_ext in [".jpg", ".jpeg", ".png"]

def set_message(msg_src):
	global len_str, bin_str, max_str

	if(not file_exists(msg_src)):
		print("   /!\\ File doesn't exist")
		print()
		return 0

	msg_str = open(msg_src, "rb").read()
	len_str = len(msg_str)
	fmt_msg = os.path.splitext(msg_src)[1]
	
	print("   +> Message length (", len_str, ")")
	if(len_str > max_str):
		print("   /!\\ Message is too long")
		return 0

	if((len(fmt_msg) - 1) > 10):
		print("   /!\\ File format is too long (Max: 10)")
		return 0

	bin_str = ""
	data_str = fmt_msg + "*" + str(len_str) + "*"
	byte_str = bytearray(data_str, "utf8") + bytearray(msg_str)
	for x in byte_str:
		bin_str += "{0:08b}".format(x)
	print()
	return 1

def set_image(img_src):
	global base_img, max_str, _menu

	if(not file_exists(img_src)):
		print("   /!\\ File doesn't exist")
		print()
		return 0

	fmt_msg = os.path.splitext(img_src)[1]
	if(not valid_image(fmt_msg)):
		print("   /!\\ Invalid file format")
		print()
		return 0

	base_img = Image.open(img_src)
	mode_img = base_img.mode
	fmt_img = base_img.format
	size_img = base_img.size

	print("   +> Dimension (", size_img[0], "x", size_img[1], ") pixel")
	print("   +> Format (", fmt_img, ")")
	print("   +> Color mode (", mode_img, ")")

	if(mode_img != "RGB"):
		print("   /!\\ Can't use image with ", mode_img, " color")
		print("   /!\\ Use image with RGB color")
		print()
		return 0
	if(_menu == "hide"):
		max_str = int((size_img[0] * size_img[1] * 3) / 8)
		max_str = max_str - len(str(max_str)) - 15
		if(max_str < 1):
			print("   /!\\ Image dimension is too small")
		print("   +> Max message length (", max_str, ") !important")
	print()
	return 1

def hide_message(out_src):
	global base_img, bin_str

	array_img = asarray(base_img)
	array_img = array_img.copy()

	i_char = 0
	len_char = len(bin_str)
	is_char = True
	for h in range(len(array_img)):
		if(not is_char): break
		for w in range(len(array_img[h])):
			if(not is_char): break
			for c in range(len(array_img[h][w])):
				if(not is_char): break
				bin_color = "{0:08b}".format(array_img[h][w][c])
				new_color = bin_color[0:7] + bin_str[i_char]
				array_img[h][w][c] = int(new_color, 2)

				i_char += 1
				if(i_char == len_char): is_char = False

	if(not is_char):
		steg_img = Image.fromarray(array_img)
		steg_img.save(out_src)
		print("   (!) Done. Output file (", out_src, ")")
		print()

def read_message(img_src):
	global base_img

	set_image(img_src)

	array_img = asarray(base_img)
	array_img = array_img.copy()

	is_char = True
	is_msg = False

	d_char = ""
	n_char = 0

	mode_msg = 0

	len_msg = 0
	fmt_msg = ""
	byte_msg = b""
	for h in range(len(array_img)):
		if(not is_char): break
		for w in range(len(array_img[h])):
			if(not is_char): break
			for c in range(len(array_img[h][w])):
				if(not is_char): break
				bin_color = "{0:08b}".format(array_img[h][w][c])
				d_char += bin_color[7:8]
				n_char += 1
				if(n_char == 8):
					g_byte = bytes([int(d_char, 2)])
					if(mode_msg == 0):
						if(g_byte.decode("utf-8") == "*"):
							fmt_msg = byte_msg.decode("utf-8")
							if(fmt_msg[0] == "." or fmt_msg == "" and len(fmt_msg) <= 10):
								print("   +> Detected file format (", fmt_msg, ")")
								byte_msg = b""
								mode_msg = 1
							else:
								is_char = False
						else:
							byte_msg += g_byte
					elif(mode_msg == 1):
						if(g_byte.decode("utf-8") == "*"):
							len_msg = int(byte_msg.decode("utf-8"))
							print("   +> Message length (", len_msg, ")")
							byte_msg = b""
							mode_msg = 2
							is_msg = True
						else:
							byte_msg += g_byte
					elif(mode_msg == 2):
						byte_msg += g_byte
						len_msg -= 1
						if(len_msg == 0): is_char = False
					
					n_char = 0
					d_char = ""
	print()
	if(not is_char and is_msg):
		out_name = input("+--Output filename (default = steg_message)\n+--> ")
		out_name = "steg_message" if(out_name=="") else(out_name)

		out_src = out_name + fmt_msg
		msg_file = open(out_src, "wb")
		msg_file.write(byte_msg)
		msg_file.close()
		print("   (!) Done. Output file (", out_src, ")")
	else:
		print("   (!) Can't read or no hidden message")
	print()

def show_banner_menu():
	print("""
+--------+      +--------+ 
|00110010|      | __  () |
|01001101| __\\  |/  \\ __ |
|11001000|   /  |____/__\\|
|01000101|      |+ ./:| .|
+--------+      +--------+

RGB Steganografi (beta)
+------------------------+
""")

def show_help_menu():
	print("""
Command
---------------
    help          Show available command.
    hide          Hide message into image.
    read          Read hidden message from image.
    exit          Exit RGB Steganografi.
""")

def show_hide_menu():
	print("""
+------------------------+
       Hide Message
+------------------------+
""")
	_img_ok = 0
	while(_img_ok != 1):
		_img_path = input("+--Image file path (Image with RGB Color)\n+--> ")
		_img_ok = set_image(_img_path)

	_msg_ok = 0
	while(_msg_ok != 1):
		_msg_path = input("+--Message file path (Image with RGB Color)\n+--> ")
		_msg_ok = set_message(_msg_path)
	
	_out_path = input("+--Output file path (default = steg_result.png)\n+--> ")
	_out_path = "steg_result.png" if(_out_path=="") else(_out_path)
	hide_message(_out_path)

def show_read_menu():
	print("""
+------------------------+
       Read Message
+------------------------+
""")
	_img_path = input("+--Image file path (Any File Format)\n+--> ")
	read_message(_img_path)

if __name__ == '__main__':
	global _menu
	_menu = "menu"
	while(_menu != "exit"):
		if(_menu == "menu"):   show_banner_menu()
		elif(_menu == "help"): show_help_menu()
		elif(_menu == "hide"): show_hide_menu()
		elif(_menu == "read"): show_read_menu()
		elif(_menu == "exit"): print()
		else:
			print("   /!\\ Unknown command")
			print()

		if(_menu != "exit"): _menu = input("stega > ")