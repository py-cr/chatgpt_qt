// // 开启代码高亮-->
// hljs.initHighlightingOnLoad();
// // 行号显示
// hljs.initLineNumbersOnLoad ({ singleLine:true });
// hljs.highlightAll();
his_id = 1
function i_am_saying(html, call) {
    rightTitle(his_id++,"../images/me.png", "我", "blue");
    waitUpdateHtml(html, call, 10);
}

function openai_saying(html, call) {
    leftTitle(his_id++,"../images/icon_16.png", "OpenAI", "green");
    waitUpdateHtml(html, call, 500);
}

function waitUpdateHtml(html, call, timeout) {
    updateHtml("<div class=\"loading\"></div>");
    window.setTimeout(function () {
        updateHtml(html, true);
        if (call) {
            call();
        }
    }, timeout);
}

html = "<pre><code class=\"php\">";
html += "&lt;?php\n";
html += "//使用substr_replace函数进行字符串插入操作demo\n";
html += "$str=\"欢迎来到yii666\";\n";
html += "echo substr_replace($str,\"PHP大神\",4,0);\n";
html += "//输出：欢迎\"PHP大神\"来到yii666\n";
html += "?&gt;";
html += "</code></pre>";

html1 = "<pre><code class=\"python\">";
html1 += "import os\n";
html1 += "\n";
html1 += "print(\"hello\") # world";
html1 += "</code></pre>";

html2 = "<pre><code class=\"language-python\">";
html2 += "import os\n";
html2 += "rom PyQt5.QtCore import *\n";
html2 += "from common.ui_utils import find_file\n";
html2 += "import os\n";
html2 += "\n";
html2 += "class MainWindow(QMainWindow):  # commit\n";
html2 += "    def __init__(self, *args, **kwargs):\n";
html2 += "        super().__init__(*args, **kwargs)\n";
html2 += "</code></pre>";

html3 = "<pre><code class=\"language-html\">";
html3 += "&lt;!DOCTYPE html&gt;\n";
html3 += "&lt;html&gt;\n";
html3 += "&lt;head&gt;\n";
html3 += "&lt;title&gt;Hello, World!&lt;/title&gt;\n";
html3 += "&lt;/head&gt;\n";
html3 += "&lt;body&gt;\n";
html3 += "&lt;h1&gt;Hello, World!&lt;/h1&gt;\n";
html3 += "&lt;/body&gt;\n";
html3 += "&lt;/html&gt;\n";
html3 += "\n";
html3 += "</code></pre>";

html4 = "<pre><code class=\"language-python\">";
html4 += "import os\n";
html4 += "\n";
html4 += "print(\"hello\") # world";
html4 += "</code></pre>";

html5 = "<pre><code class=\"html\">";
html5 += "&lt;!DOCTYPE html&gt;\n";
html5 += "&lt;html&gt;\n";
html5 += "&lt;head&gt;\n";
html5 += "&lt;title&gt;Hello, World!&lt;/title&gt;\n";
html5 += "&lt;/head&gt;\n";
html5 += "&lt;body&gt;\n";
html5 += "&lt;h1&gt;Hello, World!&lt;/h1&gt;\n";
html5 += "&lt;/body&gt;\n";
html5 += "&lt;/html&gt;\n";
html5 += "\n";
html5 += "</code></pre>";

// i_am_saying(html, function () {
//     openai_saying(html1, function () {
//         i_am_saying(html2, function () {
//             openai_saying(html3, false);
//         });
//     });
// });

// Promise 方式实现
function chat(func, html) {
    return new Promise(function (resolve, reject) {
        func(html, function () {
            resolve();
        });
    });
}


chat(i_am_saying, html).then(function () {
    return chat(openai_saying, html1);
}).then(function () {
    return chat(i_am_saying, html2);
}).then(function () {
    return chat(openai_saying, html3);
}).then(function () {
    return chat(i_am_saying, html4);
}).then(function () {
    return chat(openai_saying, html5);
});