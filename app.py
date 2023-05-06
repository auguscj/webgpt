# -*- coding:utf-8 -*-
import os
import logging
import sys

import gradio as gr

from modules import config
from modules.config import *
from modules.utils import *
from modules.presets import *
from modules.overwrites import *
from modules.models.models import get_model


gr.Chatbot._postprocess_chat_messages = postprocess_chat_messages
gr.Chatbot.postprocess = postprocess

with open("assets/custom.css", "r", encoding="utf-8") as f:
    customCSS = f.read()

def create_new_model():
    return get_model(model_name = MODELS[DEFAULT_MODEL], access_key = my_api_key)[0]

with gr.Blocks(css=customCSS) as demo:
    user_name = gr.State("")
    user_question = gr.State("")
    user_api_key = gr.State(my_api_key)
    current_model = gr.State(create_new_model)

    # topic = gr.State(i18n("未命名对话历史记录"))

    with gr.Row().style(equal_height=True):

        with gr.Column(scale=5):

            with gr.Row():
                chatbot = gr.Chatbot(elem_id="chuanhu_chatbot").style(height="75%")
            with gr.Row():
                with gr.Column(min_width=225, scale=12):
                    user_input = gr.Textbox(
                        elem_id="user_input_tb",
                        show_label=False, placeholder=str("在这里输入")
                    ).style(container=False)
                with gr.Column(min_width=42, scale=1):
                    submitBtn = gr.Button(value="", variant="primary", elem_id="submit_btn")
                    cancelBtn = gr.Button(value="", variant="secondary", visible=False, elem_id="cancel_btn")





        with gr.Column():
            with gr.Column(min_width=50, scale=1):
                with gr.Tab(label=("登录")):
                    username = gr.Textbox(label="username",placeholder="Enter username",max_lines=1)
                    password = gr.Textbox(label="password",placeholder="Enter password",type="password",max_lines=1)
                    status_display = gr.Markdown('')
                    loginbtn = gr.Button('submit',elem_id="login_btn")
                    testvalue = gr.Textbox(value="Notlogin",label="testvalue",visible=False)

                with gr.Tab(label=("注册")):
                    reg_username = gr.Textbox(label="用户名(字母数字下划线的组合)",placeholder="如jack001,长度6-20位",max_lines=1)
                    reg_password1 = gr.Textbox(label="密码(字母数字下划线的组合)",placeholder="长度6-20位",type="password",max_lines=1)
                    reg_password2 = gr.Textbox(label="再输一次密码",placeholder="Enter password again",type="password",max_lines=1)
                    reg_welcome = gr.Markdown('')
                    regisbtn = gr.Button('submit',elem_id="reg_btn")
                with gr.Tab(label=("充值和客服")):
                    gr.Markdown('10元50次提问,50元400次提问,100元1000次提问')
                    gr.Markdown('微信支付的时候一定要备注您的用户名,也可以加入我们的QQ群')
                    gr.Image(os.path.join(os.path.dirname(__file__), "assets/wechat.jpeg"))
                    gr.Image(os.path.join(os.path.dirname(__file__), "assets/qq_group.jpeg"))

    # demo.load(refresh_ui_elements_on_load, [current_model, username], [testvalue2], show_progress=False)
    chatgpt_predict_args = dict(
        fn=predict,
        inputs=[
            current_model,
            user_question,
            chatbot,
            testvalue
        ],
        outputs=[chatbot, status_display],
        show_progress=True,
    )

    start_outputing_args = dict(
        fn=start_outputing,
        inputs=[],
        outputs=[submitBtn, cancelBtn],
        show_progress=True,
    )

    end_outputing_args = dict(
        fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
    )

    reset_textbox_args = dict(
        fn=reset_textbox, inputs=[], outputs=[user_input]
    )

    transfer_input_args = dict(
        fn=transfer_input, inputs=[user_input], outputs=[user_question, user_input, submitBtn, cancelBtn], show_progress=True
    )


    # Chatbot
    cancelBtn.click(interrupt, [current_model], [])

    user_input.submit(**transfer_input_args).then(**chatgpt_predict_args).then(**end_outputing_args)
    # user_input.submit(**get_usage_args)

    submitBtn.click(**transfer_input_args).then(**chatgpt_predict_args).then(**end_outputing_args)
    # submitBtn.click(**get_usage_args)

    ##### login and regis##
    # loginbtn.click(fn=login, inputs=[username, password], outputs=[welcome, testvalue])
    loginbtn.click(fn=login, inputs=[username, password], outputs=[username,password,loginbtn,reg_username,reg_password1,reg_password2,regisbtn,reg_welcome,status_display,testvalue])
    regisbtn.click(fn=register, inputs=[reg_username, reg_password1,reg_password2], outputs=[reg_username,reg_password1,reg_password2,regisbtn,reg_welcome])


# 默认开启本地服务器，默认可以直接从IP访问，默认不创建公开分享链接
demo.title = str("ChatGPT")

if __name__ == "__main__":
    reload_javascript()
    demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        inbrowser=not dockerflag, # 禁止在docker下开启inbrowser
    )
