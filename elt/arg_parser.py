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
        help="Ví dụ: casimatna , anhtraisayhi, tinhhasayhi, 2ngay1dem.. chỉ hợp lệ khi chương trình thuộc đúng channel",
    )
    return parser.parse_args()
