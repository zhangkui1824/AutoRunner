import gzip
import base64
import requests
import time
import random
import re
import sys  # 系统模块，获得命令行参数
from PyQt5.QtWidgets import QApplication, \
    QMainWindow  # , QWidget, QLabel, QFormLayout  # 导入QAppliaction，QLabel以及QWidget
from new_run import Ui_Form
from pbar import Ui_ProBar

"""
    做一个循环，一次性跑完X天的，从9.21开始跑,跑到当天？

    1.获取UID
      手机登校网，设置代理10.106.57.86:8888
    2.解析包，base64,gzip
      暂时从fiddler手动获取，以base64形式复制
      后期考虑用py脚本一步到位抓取包
    3.构造数据
      1)开始时间，结束时间，持续时间
          开始时间：
          2021-09-21 18:57:34----- 1632221254
          2021-09-22 18:43:34----- 1632307414
          间隔---86162
          持续时间：16min,960s，950-1000
          结束时间:开始时间+持续时间

      2）GPS在现有包的基准上浮动
      3）设置公里数与速度
    4.POST
"""
url = "http://10.11.246.182:8029/DragonFlyServ/Api/webserver/uploadRunData"
first_begintime = 1632221254  # 2021-09-21 18:47:34
time_interval = 86400  # 24h浮动一点
last_time = 900  # 持续时间15min浮动
distance_val = 3000.0


def depack(a):
    # 一开始爬取用，现在没用了
    b = base64.b64decode(a)
    c = gzip.decompress(b).decode()
    return c


class FakeData():
    def __init__(self):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "Keep-Alive",
            "Charset": "UTF-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)",
            "Host": "10.11.246.182:8029",
            "Accept-Encoding": "gzip",
            "Content-Length": "{}"
        }
        # 每次都要自己造的数据
        self.begintime = ''
        self.endtime = ''
        self.distance = ''
        self.speed = ''
        self.usetime = ''
        self.str = ''  # 发的包的字符串形式
        self.rand_begintime = ''
        self.rand_locations = ''  # location键的值

        # 循环时要自己造的数据
        self.studentno = "'studentno':'{}',".format('2019339900028')

        # 固定的数据
        self.uid = "'uid':'',"
        self.schoolno = "'schoolno':'10338',"
        self.atttype = "'atttype':'3',"
        self.eventno = "'eventno':'801',"
        self.pointstatus = "'pointstatus':'1',"
        self.location = "'location':'30.31490234375,120.35669325086806;1631788866;null;null;4.8;null@30.31486029730903,120.3566783311632;1631788868;null;null;4.8;null@30.314741482204862,120.35666341145833;1631788871;null;null;4.55;null@30.314698350694446,120.35666748046874;1631788872;null;null;4.76;null@30.3146484375,120.35664740668403;1631788874;null;null;4.33;null@30.314622395833332,120.35664632161458;1631788875;null;null;2.81;null@30.314584418402777,120.35664442274306;1631788877;null;null;3.07;null@30.314558376736112,120.35664143880209;1631788878;null;null;2.81;null@30.31446723090278,120.35663248697917;1631788881;null;null;1.86;null@30.314440104166668,120.35662624782987;1631788882;null;null;2.97;null@30.31438720703125,120.35662027994792;1631788884;null;null;4.44;null@30.314376085069444,120.35662027994792;1631788885;null;null;1.18;null@30.314321017795137,120.35663736979167;1631788887;null;null;1.88;null@30.314278157552085,120.35663845486111;1631788888;null;null;4.71;null@30.3142431640625,120.35664632161458;1631788891;null;null;0.61;null@30.3142431640625,120.35664632161458;1631788892;null;null;0.61;null@30.314149034288196,120.35664632161458;1631788894;null;null;4.6;null@30.314132215711805,120.35664523654513;1631788895;null;null;1.88;null@30.314049207899306,120.35665337456597;1631788897;null;null;4.66;null@30.31403998480903,120.35665445963542;1631788898;null;null;0.99;null@30.314010145399305,120.35664632161458;1631788901;null;null;2.11;null@30.31400417751736,120.35664740668403;1631788902;null;null;0.6;null@30.313905978732638,120.35665445963542;1631788904;null;null;4.33;null@30.313870985243057,120.35664740668403;1631788905;null;null;3.89;null@30.313800184461805,120.35664116753472;1631788908;null;null;3.43;null@30.31377712673611,120.35665445963542;1631788908;null;null;2.8;null@30.31375,120.35668646918403;1631788911;null;null;1.86;null@30.313751356336805,120.35672824435764;1631788912;null;null;4.05;null@30.313734537760418,120.3568617078993;1631788915;null;null;4.8;null@30.313731553819444,120.35686957465278;1631788915;null;null;0.9;null@30.313709581163195,120.35695963541667;1631788918;null;null;5.66;null@30.313709581163195,120.35696750217014;1631788919;null;null;0.77;null@30.313712022569444,120.35713080512153;1631788925;null;null;2.22;null@30.313712293836804,120.35717692057291;1631788925;null;null;4.49;null@30.31371826171875,120.35725477430556;1631788928;null;null;2.99;null@30.313717176649305,120.35729220920139;1631788929;null;null;3.59;null@30.313717447916666,120.3574302842882;1631788932;null;null;1.22;null@30.313726399739583,120.35747829861111;1631788933;null;null;4.73;null@30.313763834635417,120.35754557291666;1631788935;null;null;3.59;null@30.313792860243055,120.35756239149306;1631788936;null;null;3.71;null@30.315228949652777,120.35758653428819;1631788981;null;null;0.6;null@30.315254720052085,120.35753146701389;1631788982;null;null;5.97;null@30.3153076171875,120.3574365234375;1631788984;null;null;5.43;null@30.3153076171875,120.3574365234375;1631788985;null;null;5.43;null@30.31537353515625,120.35732014973958;1631788988;null;null;4.8;null@30.31536838107639,120.35728515625;1631788989;null;null;3.36;null@30.315364312065974,120.35717529296875;1631788991;null;null;3.59;null@30.315358072916666,120.35711398654514;1631788992;null;null;5.81;null@30.315372992621526,120.35695475260417;1631788995;null;null;7.17;null@30.31538302951389,120.35690565321181;1631788996;null;null;4.8;null@30.315343695746527,120.35684651692708;1631788998;null;null;7.02;null@30.315304633246527,120.35680555555555;1631788999;null;null;5.74;null@30.31525173611111,120.35676974826389;1631789002;null;null;1.23;null@30.3152197265625,120.35674641927083;1631789003;null;null;4.09;null@30.31516547309028,120.35669840494792;1631789005;null;null;0.6;null@30.315126410590278,120.3566783311632;1631789006;null;null;4.8;null@30.315026312934027,120.35667941623264;1631789009;null;null;2.94;null@30.315026312934027,120.35667941623264;1631789010;null;null;2.94;null@30.314923502604167,120.35666937934027;1631789012;null;null;3.59;null@30.31486138237847,120.35667534722222;1631789013;null;null;6.85;null@30.314774305555556,120.35666341145833;1631789016;null;null;4.86;null@30.314741482204862,120.35666748046874;1631789016;null;null;3.59;null@30.31469645182292,120.35665825737847;1631789019;null;null;1.25;null@30.31469645182292,120.35665825737847;1631789020;null;null;1.25;null@30.314554307725693,120.35666748046874;1631789023;null;null;6.76;null@30.31454833984375,120.3566663953993;1631789023;null;null;0.6;null@30.314466417100693,120.35665825737847;1631789026;null;null;4.2;null@30.314435492621527,120.35667046440972;1631789027;null;null;3.59;null@30.314359266493057,120.35666937934027;1631789029;null;null;3.59;null@30.31434624565972,120.35666829427083;1631789030;null;null;1.4;null@30.314252387152777,120.35667344835069;1631789033;null;null;4.44;null@30.31420925564236,120.35668240017361;1631789034;null;null;4.8;null@30.314134385850693,120.35670247395834;1631789036;null;null;4.35;null@30.314092339409722,120.35669542100695;1631789037;null;null;4.61;null@30.314048394097224,120.35670030381945;1631789040;null;null;1.37;null@30.314014485677085,120.35670844184028;1631789041;null;null;3.79;null@30.313936360677083,120.35672336154514;1631789043;null;null;4.8;null@30.313894314236112,120.35673122829861;1631789044;null;null;4.8;null@30.313773328993054,120.35676839192708;1631789047;null;null;5.7;null@30.313745388454862,120.35677924262153;1631789048;null;null;3.27;null@30.313732367621526,120.35684244791666;1631789050;null;null;3.59;null@30.313733723958332,120.35689154730903;1631789051;null;null;4.8;null@30.313723687065973,120.35701361762153;1631789054;null;null;3.59;null@30.313723687065973,120.35701361762153;1631789054;null;null;3.59;null@30.313722330729167,120.35744222005208;1631789065;null;null;6.45;null@30.31375271267361,120.35751057942709;1631789067;null;null;3.59;null@30.3137646484375,120.35753933376736;1631789068;null;null;3.14;null@30.31490993923611,120.3575843641493;1631789105;null;null;4.64;null@30.31492702907986,120.3575843641493;1631789106;null;null;1.92;null@30.31497287326389,120.35757541232638;1631789108;null;null;4.38;null@30.315023057725693,120.35757432725694;1631789109;null;null;5.58;null@30.315141059027777,120.35755343967014;1631789112;null;null;5.63;null@30.315198838975693,120.35753255208333;1631789112;null;null;6.85;null@30.315283745659723,120.35748345269097;1631789115;null;null;6.63;null@30.31529269748264,120.35745849609376;1631789116;null;null;2.54;null@30.315323621961806,120.357392578125;1631789118;null;null;3.59;null@30.31534640842014,120.35732720269097;1631789119;null;null;6.76;null@30.315355360243057,120.35724609375;1631789122;null;null;1.3;null@30.315360514322915,120.3572132703993;1631789123;null;null;3.19;null@30.31537109375,120.35713189019097;1631789125;null;null;4.17;null@30.31537624782986,120.3570738389757;1631789126;null;null;5.53;null@30.315392795138887,120.35693169487847;1631789129;null;null;3.59;null@30.315392795138887,120.35693169487847;1631789130;null;null;3.59;null@30.315384657118056,120.35680962456597;1631789132;null;null;4.31;null@30.315369737413196,120.35678168402778;1631789133;null;null;3.94;null@30.315283745659723,120.35674723307292;1631789135;null;null;5.68;null@30.31522650824653,120.35673529730903;1631789136;null;null;6.4;null@30.315127766927084,120.35673231336806;1631789139;null;null;6.72;null@30.315127766927084,120.35673231336806;1631789140;null;null;6.72;null@30.315015462239582,120.35669731987848;1631789142;null;null;6.1;null@30.31498345269097,120.356689453125;1631789143;null;null;3.59;null@30.314904513888887,120.35668538411458;1631789146;null;null;5.0;null@30.314871419270833,120.35668023003473;1631789147;null;null;3.59;null@30.31477837456597,120.35666124131944;1631789149;null;null;2.03;null@30.314735514322916,120.35666042751735;1631789150;null;null;4.68;null@30.314652506510416,120.35664143880209;1631789153;null;null;5.68;null@30.314591471354166,120.35663736979167;1631789154;null;null;6.74;null@30.314466417100693,120.35664523654513;1631789156;null;null;3.59;null@30.31443332248264,120.35664523654513;1631789157;null;null;3.59;null@30.314326985677084,120.35663140190972;1631789160;null;null;6.46;null@30.31427001953125,120.35662326388889;1631789161;null;null;6.27;null@30.314159071180555,120.35665147569445;1631789163;null;null;3.59;null@30.314159071180555,120.35665147569445;1631789164;null;null;3.59;null@30.314062228732638,120.35666124131944;1631789167;null;null;3.59;null@30.31399929470486,120.35667344835069;1631789168;null;null;7.07;null@30.313915201822915,120.35666748046874;1631789170;null;null;5.7;null@30.313879123263888,120.35667344835069;1631789171;null;null;4.04;null@30.313770073784724,120.35665445963542;1631789173;null;null;5.06;null@30.313770073784724,120.35665445963542;1631789174;null;null;5.06;null@30.313741319444443,120.35674343532986;1631789177;null;null;3.59;null@30.313724500868055,120.35679226345486;1631789178;null;null;5.12;null@30.31371554904514,120.35691460503472;1631789181;null;null;5.14;null@30.313711208767362,120.35728325737847;1631789188;null;null;5.84;null@30.313719346788194,120.35744710286458;1631789191;null;null;3.59;null@30.313717719184027,120.3575084092882;1631789192;null;null;5.9;null@30.31378879123264,120.35757649739584;1631789195;null;null;6.49;null@30.315221896701388,120.35759874131945;1631789237;null;null;1.19;null@30.31526177300347,120.35751654730903;1631789240;null;null;0.83;null@30.315267740885417,120.35750732421874;1631789241;null;null;1.05;null@30.315278862847222,120.35748942057292;1631789243;null;null;0.82;null@30.315310601128473,120.35745551215278;1631789244;null;null;4.8;null@30.31535454644097,120.35736029730903;1631789247;null;null;2.04;null@30.315365397135416,120.35734619140625;1631789248;null;null;1.86;null@30.31537353515625,120.3573060438368;1631789251;null;null;3.4;null@30.315364583333334,120.35725721571181;1631789251;null;null;4.8;null@30.31536810980903,120.35717013888889;1631789254;null;null;4.8;null@30.315380316840276,120.35712185329861;1631789255;null;null;4.8;null@30.31537326388889,120.35706488715277;1631789258;null;null;4.8;null@30.315372178819445,120.35705702039931;1631789258;null;null;0.69;null@30.315388997395832,120.35694769965278;1631789261;null;null;4.8;null@30.315389811197917,120.35689751519097;1631789262;null;null;4.8;null@30.31534966362847,120.35685872395834;1631789265;null;null;0.76;null@30.315328776041667,120.35683268229167;1631789266;null;null;3.36;null@30.315254720052085,120.35677571614583;1631789268;null;null;1.8;null@30.315242784288195,120.35676025390624;1631789269;null;null;1.86;null@30.315206434461807,120.35673448350694;1631789272;null;null;3.59;null@30.315194498697917,120.3567222764757;1631789273;null;null;1.65;null@30.31512939453125,120.3566783311632;1631789275;null;null;3.59;null@30.315123426649304,120.35667643229166;1631789276;null;null;0.61;null@30.314992404513887,120.35666531032986;1631789279;null;null;5.89;null@30.314950358072917,120.35665228949652;1631789279;null;null;4.8;null@30.314876302083334,120.35665825737847;1631789282;null;null;3.59;null@30.314855414496527,120.35665445963542;1631789283;null;null;2.25;null@30.31473931206597,120.35664849175348;1631789285;null;null;3.59;null@30.31473931206597,120.35664849175348;1631789286;null;null;3.59;null@30.31465033637153,120.35666341145833;1631789289;null;null;2.74;null@30.314619411892362,120.35666829427083;1631789290;null;null;3.59;null@30.314539388020833,120.35667344835069;1631789292;null;null;5.23;null@30.31450737847222,120.3566663953993;1631789293;null;null;3.59;null@30.31439724392361,120.35668348524305;1631789296;null;null;3.73;null@30.314381510416666,120.35668131510417;1631789297;null;null;1.71;null@30.3143212890625,120.35668836805556;1631789299;null;null;3.59;null@30.31428249782986,120.35668538411458;1631789300;null;null;4.29;null@30.314190266927085,120.35669731987848;1631789303;null;null;4.8;null@30.314190266927085,120.35669731987848;1631789304;null;null;4.8;null@30.31405734592014,120.35671332465277;1631789306;null;null;7.14;null@30.314024251302083,120.35671223958333;1631789307;null;null;3.59;null@30.313960503472224,120.35672336154514;1631789310;null;null;2.59;null@30.313928493923612,120.35673231336806;1631789310;null;null;3.59;null@30.313812391493055,120.35675238715278;1631789313;null;null;3.05;null@30.313766276041665,120.35678548177083;1631789314;null;null;5.98;null@30.313737250434027,120.35681640625;1631789317;null;null;3.1;null@30.313729654947917,120.35687065972222;1631789317;null;null;5.33;null@30.313733723958332,120.35699462890625;1631789320;null;null;2.38;null@30.31373291015625,120.35703152126736;1631789321;null;null;3.59;null@30.313718804253472,120.35710503472222;1631789324;null;null;3.59;null@30.313717990451387,120.35714192708333;1631789324;null;null;3.59;null@30.31370659722222,120.35744113498264;1631789335;null;null;0.79;null@30.313748643663196,120.35752332899305;1631789337;null;null;2.78;null@30.313748643663196,120.35752332899305;1631789338;null;null;2.78;null@30.313783637152778,120.35758246527777;1631789341;null;null;0.77;null@30.31486111111111,120.35758843315972;1631789376;null;null;3.59;null@30.31497287326389,120.35756754557292;1631789379;null;null;4.13;null@30.315003797743056,120.35756049262153;1631789380;null;null;3.59;null@30.315069986979168,120.35755832248265;1631789382;null;null;2.41;null@30.315078125,120.35755750868056;1631789383;null;null;0.99;null@30.315182834201387,120.35753445095486;1631789386;null;null;2.77;null@30.315187717013888,120.35753336588542;1631789387;null;null;0.6;null@30.315249837239584,120.35752251519098;1631789389;null;null;6.54;null@30.315278862847222,120.3574853515625;1631789390;null;null;4.8;null@30.31533365885417,120.35739149305556;1631789393;null;null;1.32;null@30.31533365885417,120.35739149305556;1631789394;null;null;1.32;null@30.31535454644097,120.35722927517361;1631789396;null;null;5.75;null@30.315352105034723,120.35717909071181;1631789397;null;null;4.76;null@30.315360243055554,120.35713297526041;1631789400;null;null;0.82;null@30.315365125868055,120.35708279079861;1631789401;null;null;4.8;null@30.315376790364585,120.35697184244792;1631789403;null;null;3.59;null@30.315380045572915,120.35695258246528;1631789404;null;null;1.87;null@30.315374620225693,120.35684163411459;1631789407;null;null;6.95;null@30.315381673177082,120.35680474175348;1631789408;null;null;3.59;null@30.315308702256946,120.35674424913195;1631789410;null;null;3.72;null@30.315274522569446,120.35674235026042;1631789411;null;null;3.67;null@30.31520534939236,120.35672037760416;1631789414;null;null;4.22;null@30.315184461805554,120.35672037760416;1631789415;null;null;2.24;null@30.315127766927084,120.35673231336806;1631789417;null;null;5.98;null@30.31508544921875,120.35671847873265;1631789418;null;null;4.8;null@30.314998372395834,120.35672037760416;1631789421;null;null;4.8;null@30.314986436631944,120.35671440972222;1631789422;null;null;1.35;null@30.314881456163196,120.35670545789931;1631789424;null;null;4.8;null@30.314843478732637,120.35668728298612;1631789425;null;null;4.52;null@30.314776475694444,120.35666937934027;1631789428;null;null;2.76;null@30.31471137152778,120.35666829427083;1631789429;null;null;7.19;null@30.314585503472223,120.35663628472223;1631789431;null;null;7.04;null@30.314585503472223,120.35663628472223;1631789432;null;null;7.04;null@30.314462076822917,120.35661946614583;1631789435;null;null;4.04;null@30.31444118923611,120.35662136501736;1631789436;null;null;2.26;null@30.314398057725693,120.35663031684028;1631789438;null;null;0.6;null@30.314349500868055,120.35664632161458;1631789439;null;null;5.64;null@30.31426242404514,120.3566574435764;1631789442;null;null;3.59;null@30.314211154513888,120.35665228949652;1631789443;null;null;5.67;null@30.314123263888888,120.35666232638889;1631789445;null;null;3.6;null@30.314117296006945,120.35666232638889;1631789446;null;null;0.6;null@30.313990071614583,120.35663845486111;1631789449;null;null;3.59;null@30.31395697699653,120.35664632161458;1631789450;null;null;3.7;null@30.31383816189236,120.35663113064236;1631789452;null;null;6.8;null@30.313786078559026,120.35665337456597;1631789453;null;null;6.12;null@30.3137353515625,120.35675130208334;1631789456;null;null;6.23;null@30.313724500868055,120.35681125217013;1631789457;null;null;5.95;null@30.313719618055554,120.35687364366319;1631789460;null;null;2.3;null@30.313712565104165,120.35692274305555;1631789460;null;null;4.8;null@30.3137109375,120.3571080186632;1631789464;null;null;3.59;null@30.31371826171875,120.35718098958333;1631789466;null;null;3.59;null@30.313710123697916,120.357216796875;1631789467;null;null;3.59;null@30.31371310763889,120.35733615451389;1631789470;null;null;4.49;null@30.31371310763889,120.35733615451389;1631789471;null;null;4.49;null@30.3137158203125,120.35750949435764;1631789473;null;null;4.37;null@30.313760850694443,120.35753933376736;1631789474;null;null;6.13;null@30.315252007378472,120.35754855685764;1631789515;null;null;3.59;null@30.31526882595486,120.35751654730903;1631789516;null;null;3.59;null@30.315323621961806,120.3573974609375;1631789519;null;null;5.01;null@30.315325792100694,120.35739149305556;1631789520;null;null;0.6;null@30.315371365017363,120.3572962782118;1631789523;null;null;4.69;null@30.315377332899306,120.35725911458333;1631789523;null;null;3.59;null@30.31536810980903,120.35711398654514;1631789526;null;null;4.84;null@30.315365939670137,120.35704698350695;1631789527;null;null;6.34;null@30.315362955729167,120.35697102864583;1631789530;null;null;3.59;null@30.315377875434027,120.35693657769097;1631789530;null;null;3.59;null@30.31532172309028,120.35683268229167;1631789533;null;null;5.82;null@30.31529052734375,120.35681857638889;1631789534;null;null;3.59;null@30.315237630208333,120.35677354600695;1631789537;null;null;3.59;null@30.315210774739583,120.35675048828125;1631789537;null;null;3.63;null@30.31513237847222,120.3566783311632;1631789540;null;null;3.59;null@30.31513237847222,120.3566783311632;1631789541;null;null;3.59;null@30.31501437717014,120.35667534722222;1631789543;null;null;3.59;null@30.314952256944444,120.35667344835069;1631789544;null;null;6.86;null@30.31484537760417,120.35666042751735;1631789547;null;null;3.59;null@30.31484537760417,120.35666042751735;1631789548;null;null;3.59;null@30.31474636501736,120.35665934244791;1631789550;null;null;3.59;null@30.314683430989582,120.35667236328125;1631789551;null;null;7.08;null@30.31460150824653,120.35665934244791;1631789554;null;null;3.88;null@30.31456841362847,120.35666829427083;1631789555;null;null;3.73;null@30.314420301649307,120.35667941623264;1631789558;null;null;3.59;null@30.314381510416666,120.356689453125;1631789558;null;null;4.36;null@30.314285481770835,120.35667344835069;1631789561;null;null;7.0;null@30.314253472222223,120.35668348524305;1631789562;null;null;3.59;null@30.314127332899307,120.35671332465277;1631789564;null;null;3.59;null@30.314127332899307,120.35671332465277;1631789565;null;null;3.59;null@30.31400146484375,120.35672336154514;1631789568;null;null;3.59;null@30.313958333333332,120.35672526041667;1631789569;null;null;4.68;null@30.313895399305554,120.35673231336806;1631789571;null;null;3.59;null@30.313849283854168,120.35675726996527;1631789572;null;null;5.57;null@30.31374240451389,120.35682942708333;1631789575;null;null;5.35;null@30.313722601996528,120.35688557942709;1631789576;null;null;5.79;null@30.313711751302083,120.35699354383681;1631789578;null;null;6.72;null@30.313715006510417,120.35705376519097;1631789579;null;null;5.78;null@30.313719346788194,120.357451171875;1631789592;null;null;1.32;null@30.31372856987847,120.35747504340277;1631789593;null;null;2.54;null@30.313734537760418,120.35749837239584;1631789596;null;null;1.84;null@30.313753797743054,120.35754231770834;1631789596;null;null;4.8;null@30.314911024305555,120.35758843315972;1631789641;null;null;0.82;null@30.314947916666668,120.35758843315972;1631789642;null;null;4.12;null@30.31500705295139,120.35758843315972;1631789644;null;null;2.74;null@30.315026041666666,120.35758544921875;1631789645;null;null;2.14;null@30.315126953125,120.35755642361111;1631789648;null;null;5.61;null@30.315169813368055,120.35753851996527;1631789649;null;null;5.11;null@30.315225694444443,120.35753146701389;1631789651;null;null;2.49;null@30.315252821180554,120.35751546223959;1631789652;null;null;3.59;null@30.315317654079863,120.35739149305556;1631789655;null;null;4.74;null@30.315328504774307,120.35736626519098;1631789656;null;null;2.65;null@30.315337456597224,120.35727810329861;1631789659;null;null;4.33;null@30.315343424479167,120.3572412109375;1631789659;null;null;3.59;null@30.315364312065974,120.35711995442708;1631789662;null;null;3.59;null@30.31536919487847,120.35708984375;1631789663;null;null;2.91;null@30.315377875434027,120.3570179578993;1631789665;null;null;3.29;null@30.315372992621526,120.35697998046875;1631789666;null;null;3.59;null@30.315389539930557,120.35686062282986;1631789669;null;null;4.04;null@30.31538872612847,120.35685356987847;1631789670;null;null;0.6;null@30.3153857421875,120.35679660373263;1631789673;null;null;1.76;null@30.31536078559028,120.35678059895834;1631789673;null;null;3.59;null@30.315264756944444,120.35674533420139;1631789676;null;null;3.59;null@30.315264756944444,120.35674533420139;1631789677;null;null;3.59;null@30.315155436197916,120.35669623480902;1631789679;null;null;3.59;null@30.31514350043403,120.35670545789931;1631789680;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789683;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789684;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789686;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789687;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789690;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789691;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789693;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789694;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789697;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789698;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789700;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789701;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789704;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789705;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789707;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789708;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789710;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789711;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789714;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789715;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789717;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789718;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789721;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789722;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789725;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789725;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789728;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789729;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789732;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789732;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789735;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789736;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789739;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789739;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789742;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789743;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789746;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789747;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789749;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789750;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789753;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789754;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789756;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789757;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789760;null;null;6.89;null@30.31514350043403,120.35670545789931;1631789761;null;null;6.89;null',"
        self.newlocation = "'location':'{}',"
        self.locations = ''
        self.data = ''
        self.cur_dis = ''
        random.seed()

    def maketime(self, cur_begin=first_begintime):
        # 开始时间，持续时间，结束时间
        self.rand_begintime = cur_begin + random.randint(-600, 600)  # 开始时间前后浮动十分钟
        rand_last_time = last_time + random.randint(30, 300)  # 跑步时长增加半分钟到五分钟
        self.begintime = "'begintime':'{}',".format(self.rand_begintime)
        self.usetime = "'usetime':'{}.0'".format(rand_last_time)
        self.endtime = "'endtime':'{}',".format(rand_last_time + self.rand_begintime)  # 结束时间是两者相加

    def makegps(self):
        # 构造GPS点，由self.location的点随机浮动得到
        # 顺便构造跑步总距离,速度
        rand_dis = 3000.0 + round(random.uniform(10.2, 100.4), 1)
        rand_speed = 3.367003367003367 + round(random.uniform(0.3, 0.7), 8)
        self.distance = "'distance':'{}',".format(round(rand_dis, 1))
        self.speed = "'speed':'{}',".format(rand_speed)
        self.locations = self.location[12:].split('@')
        k = 0
        for i in self.locations:
            points = i.split(';')
            x = float(points[0].split(',')[0])
            y = float(points[0].split(',')[1])
            cur_time = float(points[1])
            cur_speed = float(points[4])
            randx = x + round(0.00001 * (random.randint(1, 100)), 10)
            randy = y + round(0.00001 * (random.randint(1, 100)), 10)
            randtime = float(self.rand_begintime + k)
            k = k + 1
            rand_cur_speed = abs(cur_speed + round(random.uniform(-2.2, 3.3), 2))
            cur_point_data = str(randx) + ',' + str(randy) + ';' + str(randtime) + ';null;null;' + str(
                rand_cur_speed) + ';null@'
            self.rand_locations += cur_point_data
        self.rand_locations = self.rand_locations[:-1]
        self.newlocation = "'location':'{}',".format(self.rand_locations)

    def makedata(self):
        self.str = '{' + self.begintime + self.endtime + self.uid + self.schoolno + self.distance + self.speed + self.studentno + self.atttype + self.eventno + self.newlocation + self.pointstatus + self.usetime + '}'
        # print(self.str)

    def compressdata(self):
        # 压缩字符串并设置头部的长度
        self.data = gzip.compress(self.str.encode("utf-8"), compresslevel=6)
        self.headers["Content-Length"] = str(len(self.data))

    def post_data(self):
        print("start upload")
        try:
            rep = requests.post(url=url, headers=self.headers, data=self.data, timeout=1)
        except:
            print("跑步失败")

        # print(rep.content)

    def loop_run(self, num=40):
        # 一个人40次,从21号开始算
        # print(self.uid)
        nowertime = int(time.time())
        self.set_user(wmain.lineEdit.text())
        pbarw.show()
        for i in range(0, num):
            if first_begintime + i * time_interval > nowertime:
                print("你要跑明天的吗？")
                return 0
            self.maketime(cur_begin=first_begintime + i * time_interval + random.randint(-2000, 2000))
            self.makegps()
            self.makedata()
            self.compressdata()
            self.post_data()
            wpbar.progressBar.setValue(int(3 * i))
            app.processEvents()
            for j in range(4):
                for k in range(50000000):
                    pass

    def set_user(self, user_stuno='2019339900028'):
        self.studentno = "'studentno':'{}',".format(user_stuno)
        print(self.studentno)

    def query_data(self):
        query_url = 'http://10.11.246.182:8029/DragonFlyServ/Api/webserver/getRunDataSummary'
        qheaderss = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "Keep-Alive",
            "Charset": "UTF-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)",
            "Host": "10.11.246.182:8029",
            "Accept-Encoding": "gzip",
            "Content-Length": "{}"
        }
        qdataa = gzip.compress(("{'studentno':'" + (wmain.lineEdit.text()) + "','uid':''}").encode("utf-8"),
                               compresslevel=6)
        qheaderss["Content-Length"] = str(len(qdataa))
        rep = requests.post(url=query_url, headers=qheaderss, data=qdataa)
        qcur_dis = re.findall('[:](\d+[.]\d*)', str(rep.content))
        sum = 0
        if len(qcur_dis) == 0:
            sum = 0
        else:
            for i in range(len(qcur_dis)):
                sum += float(qcur_dis[i])
        wmain.label_3.setText(str(sum) + 'km')
        wmain.progressBar1.setValue(min(int(sum), 120))


def qset_user(user_stuno='2019339900028'):
    run.studentno = "'studentno':'{}',".format(wmain.lineEdit.text())


if __name__ == '__main__':
    run = FakeData()
    app = QApplication(sys.argv)
    mainw = QMainWindow()
    wmain = Ui_Form()
    wmain.setupUi(mainw)
    wpbar = Ui_ProBar()
    pbarw = QMainWindow()
    wpbar.setupUi(pbarw)
    mainw.setFixedSize(mainw.width(), mainw.height())

    wmain.lineEdit.setText("2019339900028")
    wpbar.progressBar.setRange(0, 120)
    wmain.progressBar1.setRange(0, 120)
    wpbar.progressBar.setValue(0)
    wmain.query.clicked.connect(lambda: run.query_data())
    wmain.runrun.clicked.connect(lambda: run.loop_run())
    wmain.label_3.clear()
    mainw.show()
    app.exec()
