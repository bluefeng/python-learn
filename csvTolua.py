import os, time, csv

ROOT_DIR = os.getcwd()
CSV_DIR = os.path.join(ROOT_DIR, "documents")
LUA_DIR = os.path.join(ROOT_DIR, "csvdata")

ENCODING = "gbk"

LINE_DEFINE = {
    "FIELD": 1,
    "TYPE":2,
    "ISKEY":3,
}
ValueStartLine = 4

SUPPORT_TYPE = {
    "number" : 0,
    "string" : 1,
}

def tonumber(s):
    if isinstance(s, int) or isinstance(s, float) :
        return s
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            pass
    return 0

def parseValue(value, vtype):
    if vtype == "number":
        return tonumber(value)
    elif vtype == "string":
        return value.strip().strip("\"\'").replace('\"','\\\"').replace('\'','\\\'')

def pyToLua(data):
    def encodeOne(one, spacing = 0):
        if isinstance(one, list) or isinstance(one, tuple) :
            content = ""
            for node in one:
                content += "{}{},\n".format("\t" * (spacing + 1), encodeOne(node, spacing + 1))
            return "{{\n{}{}}}".format(content, "\t" * spacing)
        elif isinstance(one, dict):
            content = "{\n"
            for key, value in one.items():
                content += "{}[{}] = {},\n".format("\t" * (spacing + 1),encodeOne(key), encodeOne(value, spacing + 1))
            content += "\t" * spacing + "}"
            return content
        elif isinstance(one, bool):
            if one :
                return "true"
            else:
                return "false"
        elif isinstance(one, str):
            return "\"" + one + "\""
        elif isinstance(one, float) or isinstance(one, int):
            return str(one)
        elif one == None:
            return "nil"
        else:
            print("error , no handle type!!! for to lua!")
            return "error , no handle type!!! for to lua!"

    return "return {}\n".format(encodeOne(data))

ERRORS = []
hadName = {}
initList = [] 
def transOne(filePath):
    result = {}
    with open(filePath, "rb") as csvfile:
        def decoding():
            for line in csvfile:
                try:
                    yield line.decode(ENCODING)
                except:
                    yield line.decode("gbk") #备用
        lineIdx = -1
        fields = []
        types = []
        keys = []
        for line in csv.reader(decoding()):
            lineIdx += 1
            if not line: continue
            if not line[0]: continue
            if lineIdx < ValueStartLine:
                if LINE_DEFINE["FIELD"] == lineIdx:
                    fields = line
                elif LINE_DEFINE["TYPE"] == lineIdx:
                    types = line
                    for idx, field in enumerate(fields) :
                        if field and types[idx] not in SUPPORT_TYPE :
                            ERRORS.append("[ERROR:] file {} field {} type {} don't support".format(filePath, field, types[idx]))
                            return
                elif LINE_DEFINE["ISKEY"] == lineIdx:
                    for idx, isKey in enumerate(line):
                        if isKey.find("key") != -1 :
                            keys.append(idx)
                    if not keys :
                        ERRORS.append("[ERROR:] file {} no key".format(filePath))
                        return
            else:
                curKeys = []
                for idx in keys:
                    key = parseValue(line[idx], types[idx])
                    if (not key and key != 0) or (line[idx] != '0' and key == 0): #key 未填写 或者格式不正确
                        break
                    curKeys.append(key)
                if len(curKeys) != len(keys): continue

                cur = result
                for key in curKeys:
                    cur[key] = cur.get(key, {})
                    cur = cur[key]

                for idx, value in enumerate(line):
                    if fields[idx]:
                        cur[fields[idx]] = parseValue(value, types[idx])

    if not result:
        ERRORS.append("[ERROR:] file {} no data".format(filePath))
    else:
        data = pyToLua(result)
        toPath = os.path.splitext(filePath.replace(CSV_DIR, LUA_DIR, 1))[0]
        dirs, name = os.path.split(toPath)

        if name in hadName:
            ERRORS.append("[ERROR:] file {} and {} have sample name".format(filePath, hadName[name]))
        else:
            hadName[name] = filePath
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        with open(toPath + ".lua", 'w') as f:
            f.write(data)
        print("[SUCCSEE:]" + filePath)
        initList.append((name, toPath.replace(ROOT_DIR, "")[len(os.path.sep):].replace(os.path.sep, "/",)))


def getPathAllDir(path):
    for maindir, subdir, file_name_list in os.walk(path):
        for filename in file_name_list:
            if os.path.splitext(filename)[1] == ".csv":
                yield os.path.join(maindir, filename)

def saveinitFile():
    initPath = os.path.join(LUA_DIR, "init.lua")
    with open(initPath, 'w') as initFile:  
        content = "csvdb = {\n"
        for oneFile in initList:
            content += "\t[\"{}Csv\"] = require(\"{}\"),\n".format(oneFile[0], oneFile[1])
        initFile.write(content + "}")
    print("[SUCCSEE:]" + initPath)

def main():
    for filePath in getPathAllDir(CSV_DIR):
        transOne(filePath)
    saveinitFile()
                
    print("\n>>>>>>>>>>>>>>>>>> result: <<<<<<<<<<<<<<<<<<<<<\n")
    if len(ERRORS) > 0:
        print('\n'.join(ERRORS))
    else:
        print("all success parsed")

if __name__ == "__main__":
    startTime = time.time()
    main()
    print('Running time: {:.3f} Seconds'.format(time.time() - startTime))

