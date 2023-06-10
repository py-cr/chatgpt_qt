$("#html_body").css("visibility", "hidden");

function clearHtml() {
    $("#html_body").empty();
}

var scrollBottomEnable = true;

function scrollBottomEnabled() {
    scrollBottomEnable = true;
}

function scrollBottomDisabled() {
    scrollBottomEnable = false;
}

function scrollBottom() {
    if (scrollBottomEnable) {
        $("html, body").prop("scrollTop", $("#html_body").prop("scrollHeight") * 2000);
    }
}

var currentStyle = "Default";

function changeStyle(styleName) {
    hideAllItems();
    $(`link[title="${styleName}"]`).removeAttr("disabled");
    $(`link[title="${currentStyle}"]`).attr("disabled", "disabled");
    currentStyle = styleName;
    showAllItems();
    // alert(`link[title="${styleName}"]`);
}

function auto_wrap_enable() {
    // 自动换行有效
    $("html").css("overflow-x", "hidden");
    $("html").css("word-break", "break-all");
    $("html").css("word-wrap", "break-word");
    $("html").css("white-space", "normal")
    $(".content").css("word-break", "break-all");
    $(".content").css("word-wrap", "break-word");
}

function auto_wrap_disable() {
    // 自动换行无效
    $("html").css("overflow-x", "auto");
    $("html").css("word-break", "normal");
    $("html").css("word-wrap", "normal");
    $("html").css("white-space", "nowrap")
    $(".content").css("word-break", "normal");
    $(".content").css("word-wrap", "normal");
}

// auto_wrap_disable();
auto_wrap_enable();
contentDiv = null;
id_index = 0;


//
function showAllItems() {
    $("#html_body").find(".l-item, .r-item").css("visibility", "visible");
    // $("#html_body").find(".r-item").css("visibility", "visible");
}

function hideAllItems() {
    $("#html_body").find(".l-item, .r-item").css("visibility", "hidden");
}


function buildTitleElement(hisId, icon, title, color, itemClass, hidden) {
    // id_index += 1;
    id_index = hisId;
    icon = "../images/" + icon;
    titleSpan = "<span>" + title + "</span>";
    // titleSpan = "<span title='History_id=" + hisId + "'>" + title + "</span>"; // TODO:保留代码（调试用）

    if ('r-item' == itemClass) {
        titleDiv = "<div id='title_" + id_index + "' class='title' style='color:" + color + "'>" + titleSpan + "<img src='" + icon + "'/></div>";
    } else {
        titleDiv = "<div id='title_" + id_index + "' class='title' style='color:" + color + "'><img src='" + icon + "'/>" + titleSpan + "</div>";
    }
    contentDiv = "<div id='content_" + id_index + "' class='content'> </div>";
    itemDiv = "<div id='item_" + id_index + "' history_id='" + id_index + "'  class='" + itemClass + "'> </div>";

    itemDiv = $(itemDiv);
    if (hidden) {
        // 如果隐藏了，一定要通过 showAllItems 显示出来
        itemDiv.css("visibility", "hidden");
    }
    itemDiv.append($(titleDiv));
    itemDiv.append($(contentDiv));
    return itemDiv;
}

function appendTitle(hisId, icon, title, color, itemClass) {
    itemDiv = buildTitleElement(hisId, icon, title, color, itemClass, false);
    $("#html_body").append(itemDiv);
    scrollBottom();
}

function insertTitle(hisId, icon, title, color, itemClass) {
    itemDiv = buildTitleElement(hisId, icon, title, color, itemClass, true);
    itemDiv.prependTo("#html_body");
    return itemDiv;
}

function insertRightTitle(hisId, icon, title, color) {
    insertTitle(hisId, icon, title, color, "r-item");
}

function insertChatItem(hisId, isLeft, icon, title, color, html, highlightElement) {
    var itemClass = "r-item";
    if (isLeft) {
        itemClass = "l-item";
    }
    itemDiv = insertTitle(hisId, icon, title, color, itemClass);
    updateHtmlByHisId(hisId, html, highlightElement);
    return html
}

function rightTitle(hisId, icon, title, color) {
    appendTitle(hisId, icon, title, color, "r-item")
}

function leftTitle(hisId, icon, title, color) {
    appendTitle(hisId, icon, title, color, "l-item")
}

function updateHtml(html, highlightElement) {
    updateHtmlWithScrollToBottom(html, highlightElement, true);
    return html
}

function updateHtmlByHisId(hisId, html, highlightElement) {
    el = $("#content_" + hisId);
    el.html(html);
    // $(el).find("pre").each(function () {
    //     var self = $(this);
    //     alert(self);
    // }); // TODO:该代码保留
    $(el).find("pre code").each(function () {
        var self = $(this);
        class_name = self.attr("class");
        // alert(class_name); // TODO:该代码保留
        // if (class_name === undefined) {
        //     self.attr("class", "py html hljs language-javascript bash");
        // } else if (class_name.indexOf("language-python") >= 0) {
        //     self.attr("class", "py hljs language-javascript");
        // } else if (class_name.indexOf("language-html") >= 0) {
        //     self.attr("class", "hljs scss html");
        // } else if (class_name.indexOf("language-mermaid") >= 0) {
        //     self.attr("class", "html hljs language-javascript bash");
        // } else {
        //
        // }
        if (highlightElement) {
            hljs.highlightElement(self[0]);
        }
    });
    return html
}

// 更新聊天消息Html，并将滚轮移动到底部（条件是：scrollToBottom=true）
function updateHtmlWithScrollToBottom(html, highlightElement, scrollToBottom) {
    updateHtmlByHisId(id_index, html, highlightElement);
    if (scrollToBottom) {
        setTimeout("scrollBottom()", 10);
    }
    return html
}

function highlightAll() {
    hljs.highlightAll();
    pageLoaded()
}

function pageLoaded() {
    $("body").css("background-image", "none");
    $("#html_body").css("visibility", "visible");
}

document.oncontextmenu = function () {
    return false;
};

$(function () {
    // 定义右键菜单项和callback函数
    $.contextMenu({
        selector: 'body',
        items: {
            "copy": {
                name: "复制", callback: function () {
                    // 复制选中的文字到剪切板
                    document.execCommand('copy');
                }
            },
            "selectAll": {
                name: "全选", callback: function () {
                    // 选中所有文字
                    document.execCommand('selectAll'); // 选中所有文本
                }
            }
        }
    });
});
// 鼠标进入到代码块'.content pre'，将代码块对象赋值到这里
var mouse_enter_pre = null;
// 鼠标移动到代码上时显示复制按钮
$('#html_body').on('mouseenter', '.content pre', function () {
    pos = $(this).position();
    // alert($(this).find("code").attr("class")); // TODO:该代码保留
    // py hljs language-javascript
    // python hljs language-python
    // xml
    copy_btn = $(this).find("button.copy-code");
    if (copy_btn.length == 0) {
        copy_btn = $('<button title=" 复制内容到剪切板 " class="copy-code"></button>');
        copy_btn.css({'top': pos.top + 'px'});
        copy_btn.removeClass("copy-ok");
        copy_btn.addClass("copy-n");
        $(this).append(copy_btn);
    } else {
        copy_btn.css({'top': pos.top + 'px'});
        copy_btn.removeClass("copy-ok");
        copy_btn.addClass("copy-n");
        copy_btn.show();
    }
    mouse_enter_pre = $(this);
    if (mouse_enter_pre.parents("div.l-item,div.r-item").hasClass("r-item")) {
        copy_btn.css("margin", "13px 25px 5px 5px");
    } else {
        copy_btn.css("margin", "13px 42px 5px 5px");
    }
});

// 鼠标移开后，不显示复制按钮
$('#html_body').on('mouseleave', '.content pre', function () {
    copy_btn = $(this).find("button.copy-code")
    if (copy_btn.length > 0) {
        copy_btn.hide()
    }
});

// 点击复制按钮时将代码块中的内容复制到剪切板
$('#html_body').on('click', 'button.copy-code', function () {
    console.log(mouse_enter_pre.children().last());
    // alert(mouse_enter_pre.text());
    text = mouse_enter_pre[0];
    if (document.body.createTextRange) {
        var range = document.body.createTextRange();
        range.moveToElementText(text);
        range.select();
        document.execCommand('copy');
        $(this).removeClass("copy-n");
        $(this).addClass("copy-ok");
        showMessage("已复制到剪切板", 1);
    } else if (window.getSelection) {
        var selection = window.getSelection();
        var range = document.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('copy');
        $(this).removeClass("copy-n");
        $(this).addClass("copy-ok");
        showMessage("已复制到剪切板", 1);
    } else {

    }
});

/**
 * 弹出消息提示框，采用浏览器布局，位于整个页面中央，默认显示3秒
 * 后面的消息会覆盖原来的消息
 * @param message：待显示的消息
 * @param type：消息类型，0：错误消息，1：成功消息
 */
function showMessage(message, type) {
    let messageJQ = $("<div class='showMessage'>" + message + "</div>");
    if (type == 0) {
        messageJQ.addClass("showMessageError");
    } else if (type == 1) {
        messageJQ.addClass("showMessageSuccess");
    }
    // 先将原始隐藏，然后添加到页面，最后以400毫秒的速度下拉显示出来
    messageJQ.hide().appendTo("body").slideDown(200);
    // 4秒之后自动删除生成的元素
    window.setTimeout(function () {
        messageJQ.show().slideUp(200, function () {
            messageJQ.remove();
        })
    }, 2000);
}

// 是否到顶了
var isAtTop = false;
// 最顶上的元素
var topElement = null;

// 滚动到上次顶层的元素位置（加载了数据后，移动滚动条到之前的位置）
function scrollToLastTopElement() {
    // 60 是模拟滚动的惯性，往上移动
    $(window).scrollTop(topElement.offset().top - 60);
}

// 是否到顶了 setter
function setIsAtTop(value) {
    isAtTop = value;
    showAllItems();
}

// 是否到顶了 getter
function getIsAtTop() {
    return isAtTop;
}

$(document).ready(function () {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.logger = channel.objects.consoleBridge;
        window.dataBridge = channel.objects.dataBridge;
        var styles = "";
        $(`link[disabled="disabled"]`).each(function () {
            styles += $(this).attr("title") + "\n";
        });
        dataBridge.onSupportedStyles(styles);


        $(window).scroll(function () {
            if ($(window).scrollTop() == 0 && isAtTop == false) {
                isAtTop = true;
                topElement = $("#html_body").children().first();
                history_id = parseInt(topElement.attr("history_id")); // l-item
                dataBridge.onRequiredHistories(history_id);
            }
        });
    });
});