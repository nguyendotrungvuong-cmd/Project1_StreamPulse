import argparse


def arg_parse():
    parser = argparse.ArgumentParser(
        description="Chương trình phân tích dữ liệu, hãy nhập tên show của và chương trình mà bạn biết"
    )
    parser.add_argument(
        "--channel",
        type=str,
        required=True,
        help="VÍ dụ: @VieChannelOfficial hoặc là @Yeah1Show",
    )
    parser.add_argument(
        "--show",
        type=str,
        required=True,
        help="Ví dụ: The Masked Singer hoặc 2 ngày 1 đêm hoặc anh trai say hi",
    )
    return parser.parse_args()
