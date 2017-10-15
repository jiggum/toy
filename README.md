"# toy"

jsx-parser
  # parseString is the function of parse JSX inside the JS string(from file)
  # and get texts inside the JSX tags
  - string : string # JSstring
  - openSymbolStacks : array # parents symbols array
  - debug : bool # print or not
  parseString(string, openSymbolStacks=[], debug=False)
    preCondition:
      linted JSstring with default ESLint setting
    return:
      (startIndex, endIndex, contentsParsed)
