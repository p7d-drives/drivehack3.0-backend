def ConvertLinesToArray(lines, X, Y):
    answer = []
    for line in lines:
        answer.append([line['x'] * X, line['y'] * Y])
    return answer