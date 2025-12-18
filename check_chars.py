
filename = 'app/models.py'
start_line = 220
end_line = 240

with open(filename, 'rb') as f:
    content = f.readlines()

for i in range(start_line, end_line):
    if i < len(content):
        print(f"{i+1}: {repr(content[i])}")
