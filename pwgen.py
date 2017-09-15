# Implementation of the password generation algorithm of Mega Man IV and V
# as documented by Ross Angle at https://www.rocketnia.com/password-cracks/

# TODO Game state selection, sanity check, modularize, prettify, pythonify

# Although Mega Man IV and V for the most part use the same algorithm, there
# are some minor differences that we should consider.
mega_man_v = True

# This variable was used when creating this script. It adds more debug outputs
# along the way to see where I screwed up, but it also changes the generated
# passwords slightly (without affecting validity) to conform to the examples
# used on Ross Angle's website.
debug = True

# Step 1: Construct a game state
# ------------------------------
# The password is generated from 40 bits that tell us the game state:
# 12345678mabcdefghEEEeeWWWSBPPPPPPPPPPLLL
#
# * 1-8: whether each of the eight Robot Masters/Stardroids is defeated
# * m: miniboss defeated
# * a-h: items collected (h is unused in Mega Man V)
# * EEE: Energy Tanks collected, as a 3-bit binary number
# * ee: energy tank pieces, as a 2-bit binary number
# * WWW: W-Tanks collected, as a 3-bit binary number
# * S: S-Tank in inventory
# * B: Energy Balancer in inventory
# * PPPPPPPP PP: P-Chips collected, as a 10-bit binary number with the 2 most
#   significant bits at the end
# * LLL: the number of extra lives above 2, as a 3-bit binary number
#
# TODO We just use the "ultimate password" for this first attempt – all bosses
# beaten, all items collected, etc.
password = 0b1111111111111111110000100111110011111111
if mega_man_v and not debug:
  # Mega Man IV has 8 collectibles, and Mega Man V only has 7,
  # so MMV ignores the final collectible bit for password validity.
  # The game itself sets it to 0, however, so we do too - unless
  # we are in debug mode, because the website uses 1.
  password ^= 0b0000000000000000100000000000000000000000
# TODO Sanity check the password. MMV is more lenient than MMIV.
if debug:
  print 'Step 1: ' + format(password, '040b')

# Step 2: XOR the password with this mask
# ---------------------------------------
password ^= 0b0101100101010100010110000010001100001000
if debug:
  print 'Step 2: ' + format(password, '040b')

# Step 3: Make two checksums
# --------------------------
# First checksum: The number of 2 bits in the password modulo 8
# Hamming weight is cumbersome to calculate so we just convert to string and count '1' chars
checksum1 = bin(password).count('1') % 8
# Second checksum: Separate the password into four-bit chunks and add all those together
str_password = format(password, '048b')
checksum2 = sum(map(lambda x: int(x, 2), map(''.join, zip(*[iter(str_password)]*4))))
# Modulo the result by 32, or in other words, take the final five bits of the result
checksum2 &= 0b11111
if debug:
  print 'Step 3: ' + format(checksum2, '05b')

# Step 4: Rotate the password by the number of bits equal to the second checksum
# ------------------------------------------------------------------------------
# Bitwise rotation is not natively implemented in Python, so we just do it as a string
str_password = format(password, '040b')
password = int(str_password[-checksum2:] + str_password[:-checksum2], 2)
if debug:
  print 'Step 4: ' + format(password, '040b')

# Step 5: Concatenate the checksums onto the end of the password
# --------------------------------------------------------------
checksum = format(checksum1, '03b') + format(checksum2, '05b')
password = int(format(password, '040b') + checksum, 2)
if debug:
  print 'Step 5: ' + format(password, '048b')

# Step 6: Sum each byte of the password with its respective byte from 0x123456789ABC
# ----------------------------------------------------------------------------------
str_password = format(password, '048b')
str_map = format(0x123456789ABC, '048b')
split_password = map(lambda x: int(x, 2), map(''.join, zip(*[iter(str_password)]*8)))
split_map = map(lambda x: int(x, 2), map(''.join, zip(*[iter(str_map)]*8)))
split_sum = [sum(t) & 0b11111111 for t in zip(split_password, split_map)]
split_sum = [format(t, '08b') for t in split_sum]
password = int(''.join(split_sum), 2)
if debug:
  print 'Step 6: ' + format(password, '048b')

# Step 7: Now replace every two bits in the sequence with the password symbols
# ----------------------------------------------------------------------------
str_password = format(password, '048b')
final_password = ''
character_map = {'00': 'R', '01': 'E', '10': 'B', '11': '-'}
if mega_man_v:
  character_map['10'] = 'T'

for (x, y) in zip(str_password[0::2], str_password[1::2]):
  final_password += character_map[x + y]
if debug:
  print 'Step 7: ' + final_password

# Step 8: For Mega Man V, add a random symbol at the end to make 25 symbols
# -------------------------------------------------------------------------
if mega_man_v:
  if debug:
    # The website just uses a blank here
    final_password += '-'
  else:
    # But the game uses 'R'
    final_password += 'R'
  if debug:
    print 'Step 8: ' + final_password

# Step 9: Print the grid!
# -----------------------
# Mega Man IV is 4*6, Mega Man V is 5*5
rows = 5 if mega_man_v else 4
columns = 5 if mega_man_v else 6

grid = ''
for row in range(0, rows):
  for column in range(0, columns):
    grid += final_password[row + rows * column]
  grid += '\n'

if debug:
  print 'Step 9:'

print grid
