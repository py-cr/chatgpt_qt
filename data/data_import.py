import json
import os

from db.db_ops import HistoryOp
from db.db_ops import SessionOp
from db.db_ops import ConfigOp


# import chardet


def save_to_db(json_file):
    j_data = json.load(open(json_file, "r", encoding="utf-8"))
    subject = j_data['title']
    create_time = j_data['create_time'] * 1000000
    mapping = j_data['mapping']

    session_id = SessionOp.insert(subject=subject, model_id='gpt-3.5-turbo', create_time=create_time)

    for key in mapping:
        if "message" in mapping[key]:
            message = mapping[key]["message"]
            role = message["author"]["role"]
            create_time = message["create_time"] * 1000000
            content = message["content"]
            content_type = content["content_type"]
            parts = content["parts"]
            for part in parts:
                create_time += 1
                HistoryOp.insert(role, part, content_type, session_id, 0, create_time)
                # print(role, part, content_type, session_id)
        else:
            print("mapping_item", mapping[key])


# https://chat.openai.com/backend-api/conversations?offset=0&limit=20
# https://chat.openai.com/backend-api/conversation/306256a4-7108-4ac4-babb-3c4b7c9a090f
"""
/**
 * 使用httpclient调用chatGPT
 */
public class App {
    public static void main(String[] args) throws Exception {
        //通过登录chatgpt截取页面的token信息
        String au = "token";
        String sendMsg = "发送的消息";
        String user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.42";
        String json = "{\"action\":\"next\",\"messages\":[{\"id\":\"16f7cd15-5e7a-461b-8992-81a80ae770fa\",\"role\":\"user\",\"content\":{\"content_type\":\"text\",\"parts\":[\"" + sendMsg + "\"]}}],\"conversation_id\":\"add24670-9871-421a-bf23-e210b5021099\",\"parent_message_id\":\"c743b493-c2dc-454e-aacd-9ce90cb1ee97\",\"model\":\"text-davinci-002-render\"}";
        System.out.println(json);
        HttpPost httpPost = new HttpPost("https://chat.openai.com/backend-api/conversation");
        httpPost.addHeader("authorization", au);
        httpPost.addHeader("user-agent", user_agent);
        httpPost.setHeader("Content-type", "application/json; charset=utf-8");
        httpPost.setEntity(new StringEntity(json, StandardCharsets.UTF_8));
        CloseableHttpClient httpClient = HttpClients.createDefault();
        CloseableHttpResponse response = httpClient.execute(httpPost);
        String body = EntityUtils.toString(response.getEntity(), StandardCharsets.UTF_8);
        String[] splitR = body.split("\n\n");
        String replaceFirst = splitR[splitR.length - 2].replaceFirst("data: ", "");
        String res = JSON.parseObject(replaceFirst).getJSONObject("message").getJSONObject("content").getJSONArray("parts").getString(0);
        System.out.println(res);
    }
}
"""


def data_import():
    root_dir = os.path.join(".", "chat_json")

    for fd in os.listdir(root_dir):
        if fd.endswith("list.json"):
            continue
        if fd.endswith(".json"):
            json_file = os.path.join(root_dir, fd)
            save_to_db(json_file)
            print(json_file)
            # break


def read_data():
    import requests
    api_key = ConfigOp.get_sys_config("api_key")
    url = "https://chat.openai.com/backend-api/conversations?offset=0&limit=20"
    # data = {
    #     "kw": word,
    # }
    # headers = {
    #     }
    proxies = {
        "http": "socks5h://127.0.0.1:10010",
        "https": "socks5h://127.0.0.1:10010",
    }
    data = {}
    headers = {
        'User-Agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 96.0.4664 .93 Safari / 537.36",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers, proxies=proxies)

    # resp = requests.get(url=url, data=data, headers=headers)
    print(response.json())


if __name__ == '__main__':
    # data_import()
    # read_data()
    pass
