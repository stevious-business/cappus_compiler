def get_data_from_file(file_obj):
    return "".join(file_obj.readlines())


def remove_comments(text: str) -> str:
    # TODO: Reimplement this as an FSM; maybe make FSM class for future
    clean_code = ""
    NOT_IN_COMMENT = 0
    MAY_BE_COMMENT = 1
    MAY_EXIT_COMMENT = 2    # this is only important for block comments
    INLINE_COMMENT = 3
    BLOCK_COMMENT = 4
    comment_status = NOT_IN_COMMENT
    for char in text:
        if comment_status is NOT_IN_COMMENT:
            if char == "/":
                comment_status = MAY_BE_COMMENT
            else:
                clean_code = clean_code + char
        elif comment_status is MAY_BE_COMMENT:
            if char == "/":
                comment_status = INLINE_COMMENT
            elif char == "*":
                comment_status = BLOCK_COMMENT
            else:
                comment_status = NOT_IN_COMMENT
                clean_code = clean_code + "/" + char
        elif comment_status is INLINE_COMMENT:
            if char == "\n":
                comment_status = NOT_IN_COMMENT
                clean_code = clean_code + "\n"
        elif comment_status is BLOCK_COMMENT:
            if char == "*":
                comment_status = MAY_EXIT_COMMENT
        elif comment_status is MAY_EXIT_COMMENT:
            if char == "/":
                comment_status = NOT_IN_COMMENT
            elif char != "*":   # if we have "...**..." keep may_exit_comment
                comment_status = BLOCK_COMMENT
    assert comment_status is not BLOCK_COMMENT, "Unclosed comment"
    assert comment_status is not MAY_EXIT_COMMENT, "Unclosed comment"
    return clean_code


def preprocess_code(text: str) -> str:
    commentfree_text = remove_comments(text)
    return commentfree_text


def preprocessed_code_from_file(file_obj) -> str:
    raw_text = get_data_from_file(file_obj)
    return preprocess_code(raw_text)