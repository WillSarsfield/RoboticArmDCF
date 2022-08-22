
a_text,b_text,c_text = '0,0', '1,1', '2,2'
a_coords,b_coords,c_coords = (text.split(',') for text in (a_text,b_text,c_text))

print(a_coords,b_coords,c_coords)