from users.models import UserProfile
from django import forms
from captcha.fields import CaptchaField  # 验证码


class LoginForm(forms.Form):
    """登录表单验证"""
    username = forms.CharField(required=True)
    # min_length定义输入值小于5位
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    """注册表单"""
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ActiveForm(forms.Form):
    """激活时验证码"""
    # 激活时不对邮箱密码做验证
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ForgetForm(forms.Form):
    """忘记密码"""
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    """重置密码form"""
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    """文件上传，修改头像"""
    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    """个人中心修改个人信息"""
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birthday', 'address', 'mobile']