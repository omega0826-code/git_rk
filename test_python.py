"""
간단한 테스트 - 파일 생성 확인
"""
with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('Python 실행 성공!\n')
    f.write('파일 생성 테스트 완료\n')

print("테스트 완료!")
