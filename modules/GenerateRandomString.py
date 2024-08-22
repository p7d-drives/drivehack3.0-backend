import random
import string

def RandomString():
    answer = ""
    for i in range(16):
        answer += random.choice(string.ascii_letters + string.digits)
    return answer + ".mp4"