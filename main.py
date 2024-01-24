from zhipuai import ZhipuAI
import requests
import concurrent.futures
from decouple import config


def find_synonyms(word, client):
    prompt = f"""你作为一个杰出的语文老师，现在你需要帮我进行语言同义词回答，请仅提供相关性最高的前10个同义词，同义词之间请用逗号‘,’隔开，请严格按照格式要求完成。
    
样例1
Q: 夏天
A: 夏日, 严夏, 热夏, 夏季

样例2
Q: 开心
A: 快乐, 高兴, 乐呵呵

Q: {word}
A: 
"""
    try:
        response = client.chat.completions.create(
            model="glm-3-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.1,
            max_tokens=1024,
            stream=False,
        )

    except requests.exceptions.RequestException as e:
        print(f"请求API时发生错误: {e}")
        return []

    # 遍历所有choices元素
    all_synonyms = []
    for choice in response.choices:
        # 提取每个choice的文本内容
        content = choice.message.content

        # 分割同义词
        synonyms = content.split(',')
        all_synonyms.extend([synonym.strip() for synonym in synonyms])

    # 去除重复的同义词
    all_synonyms = list(set(all_synonyms))
    return all_synonyms


def batch_find_synonyms(words, concurrency=2):
    synonyms_dict = {}
    apiKey = config('API_KEY')
    client = ZhipuAI(api_key=apiKey)
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_word = {executor.submit(find_synonyms, word, client): word for word in words}
        for future in concurrent.futures.as_completed(future_to_word):
            word = future_to_word[future]
            try:
                synonyms = future.result()
                synonyms_dict[word] = synonyms
            except Exception as e:
                print(f"获取'{word}'的同义词时出错: {e}")
    return synonyms_dict


def main():
    words = ["夏天", "国庆节", "春节", "模板"]  # 示例关键词列表
    concurrency = 2  # 可以根据需要调整并发度
    synonyms_dict = batch_find_synonyms(words, concurrency=concurrency)

    for word, synonyms in synonyms_dict.items():
        print(f"‘{word}’的同义词: {synonyms}")


if __name__ == "__main__":
    main()
