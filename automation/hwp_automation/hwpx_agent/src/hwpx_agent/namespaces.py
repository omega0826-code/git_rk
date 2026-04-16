from lxml import etree


NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hp10": "http://www.hancom.co.kr/hwpml/2016/paragraph",
    "ha": "http://www.hancom.co.kr/hwpml/2011/app",
    "hm": "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf": "http://www.hancom.co.kr/schema/2011/hpf",
    "hhs": "http://www.hancom.co.kr/hwpml/2011/history",
    "opf": "http://www.idpf.org/2007/opf/"
}


def tag(ns_prefix: str, local_name: str) -> str:
    return f"{{{NS[ns_prefix]}}}{local_name}"


def local_name(tag_name: str) -> str:
    return etree.QName(tag_name).localname if isinstance(tag_name, str) else ""
