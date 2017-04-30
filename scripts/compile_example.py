# -*- coding: utf-8 -*-

# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


## how to call this script
##
## fix the TEXBIN config variable in  exam_tools/settings.py  to the location of latex on your machine
## ```export PYTHONPATH=.:$PYTHONPATH```
## call the testing script
## ```python scripts/compile_example.py```


import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse

from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode
from ipho_exam.models import Exam, Question, Student, Language
from hashlib import md5
import requests


exam = Exam()
exam.code = 'E'
exam.name = 'Test template'

question = Question()
question.code = 'A'
question.name = 'Some question'
question.position = 2

student = Student()
student.code = 'XYZ-S-3'
student.first_name = 'Smart'
student.last_name = 'Student'

language = Language()
language.name = u'Taiwanese'
language.font = 'notosanstc'
language.style = 'chinese'
language.polyglossia_options = ''
language.polyglossia = 'custom'
language.extraheader = ''


# Exported from Exam Tools
doc_content = ur"""
\begin{PR}{兩個力學問題兩個力學問題兩個力學問題兩個力學問題兩個力學問題兩個力學問題兩個力學問題兩個力學問題(10分)}{10}

在開始作答之前，請先細讀另一信封袋內的「理論考試通用指引」。

\PT{A部分. 隱藏的圓盤 (3.5分)}{3.5}

考慮一個半徑\(r_1\)、厚度\(h_1\)的木頭圓柱體，在其內部某處嵌置有一個半徑\(r_2\)、厚度\(h_2\)的金屬圓盤，此圓盤的對稱軸\(B\)與木頭圓柱體的對稱軸\(S\)彼此平行，且圓盤到圓柱體頂部與底部兩個表面的距離相等。令對稱軸\(S\)與\(B\)的距離為\(d\)，木頭的密度為\(\rho_1\)，金屬的密度為\(\rho_2 > \rho_1\)。木頭圓柱體加上內部金屬圓盤的總質量為\(M\)。

在本題中，我們將圓柱體平放於地面上，使其可以左右自由滾動。圖1顯示它的側視圖與俯視圖。

本題的目標是要求出金屬圓盤的尺寸與位置。

以下你要求你以已知量表示結果時，你可假設下列各量為已知量：

\begin{equation}
r_1,~h_1,~\rho_1,~\rho_2, M~.\end{equation}

本題的目標是要經由一些間接的測量，以決定\(r_2,h_2\)及\(d\)。

\vspace{0.5cm}\begin{minipage}{\textwidth}\centering

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{圖1：a)側視圖 與b)俯視圖}
\end{minipage}\vspace{0.5cm}

整個系統的質心\(C\)到圓柱體對稱軸\(S\)的距離為\(b\)。為了決定這個距離，我們設計了以下的實驗：我們先將圓柱體擺放到一個水平基座上，使它處於穩定平衡狀態。然後慢慢的使基座傾斜一個角度\(\Theta\)(見圖2)。由於靜摩擦力的作用，圓柱體可以自由作純滾動而不致滑動。經由測量，圓柱體在往下稍微滾動一個角度\(\phi\)後，會停止不動，而處於穩定平衡狀態。

\vspace{0.5cm}\begin{minipage}{\textwidth}\centering

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{圖2：在傾斜基座上的圓柱體。}
\end{minipage}\vspace{0.5cm}

\begin{QTF}{0.8}{A}{1}
試將\(b\)表示為角度\(\phi\)、傾斜角\(\Theta\)與(1)式所示已知量的函數。


\end{QTF}

自此之後，我們將假設\(b\)的值為已知。


\vspace{0.5cm}\begin{minipage}{\textwidth}\centering

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{圖3：懸吊的系統}
\end{minipage}\vspace{0.5cm}

接著，我們想要求出圓柱體繞其對稱軸\(S\)的轉動慣量\(I_S\)。為此，我們吊起它的對稱軸，使圓柱體\(S\)軸與水平面平行懸掛。然後使它偏離平衡位置一個角度\(\varphi\)後，再放開它。實驗裝置圖請參見圖3。我們發現\(\varphi\)所描述的是一個週期為\(T\)的週期性運動。


\begin{QTF}{0.5}{A}{2}
求角度\(\varphi\)所滿足的運動方程式。試將圓柱體繞其對稱軸\(S\)的轉動慣量\(I_S\)，以\(T\)、\(b\)與(1)式中的已知量表示。你可假設我們對平衡位置的擾動很微小，以至於\(\varphi\)總是很小。

\end{QTF}

由\textbf{A.1}與\textbf{A.2}兩題所作的測量，我們現在想決定圓柱體內圓盤的位置與幾何形狀。

\begin{QTF}{0.4}{A}{3}
試將距離\(d\)表示為\(b\)與(1)式所示已知量的函數。你的表示式中所含的變數，可以包括以下\textbf{A.5}題即將計算的\(r_2\)與\(h_2\)。

\end{QTF}

\begin{QTF}{0.7}{A}{4}
試將轉動慣量\(I_S\)表示為\(b\)與(1)式所示已知量的函數。你的表示式中所含的變數，可以包括以下\textbf{A.5}題即將計算的\(r_2\)與\(h_2\)。

\end{QTF}

\begin{QTF}{1.1}{A}{5}
利用以上得到的所有結果，試將\(h_2\)與\(r_2\)表示為\(b\)、\(T\)與(1)式所示已知量的函數。你可以用\(r_2\)的函數來表示\(h_2\)。

\end{QTF}

\PT{B部分. 轉動的太空站 (6.5 分)}{6.5}

太空人艾莉絲居住在太空站裡。太空站是一個半徑為\(R\)的巨大輪子，藉由繞著它的中心軸旋轉，以提供太空人一種人造的重力加速度。太空人在輪輞(輪的邊緣)的內側表面上(以下簡稱太空站底面)，進行各種活動。此太空站很輕，故不需考慮它的重力效應。

\begin{QTF}{0.5}{B}{1}
如果太空人感受到與在地球表面一樣的重力\(g_E\)，則太空站轉動的角頻率 \(\omega_{ss}\) 為何？

\end{QTF}

艾莉絲與另一位太空人巴柏，有一點爭論。巴柏認為他們是在地球表面上，而不是在太空站內。艾莉絲想要運用物理，證明他們確實是生活在太空站中；因此她將一個質量為\(m\)的質點，連接於力常數為\(k\)的彈簧，並使其振盪。彈簧僅能沿太空站的垂直方向(輪的徑向)振盪，沿水平方向無法移動。

\begin{QTF}{0.2}{B}{2}
假設地球的重力加速度\(g_E\)為一常數，則此彈簧在地球表面上振盪時的角頻率\(\omega_E\)為何？

\end{QTF}

\begin{QTF}{0.6}{B}{3}
在太空站上，艾莉絲測得彈簧振盪的角頻率\(\omega\)為何？

\end{QTF}

艾莉絲確認她的實驗證明他們是生活在太空站上。但包柏還是半信半疑，他強調：如果考慮在地表之上之重力加速度隨高度的變化，也會出現類似於太空站的效果。他是對的嗎？


\vspace{0.5cm}\begin{minipage}{\textwidth}\centering

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{圖4:太空站}
\end{minipage}\vspace{0.5cm}

\begin{QTF}{0.8}{B}{4}
當在地表上的高度\(h\)不大時，重力加速度的表達式\(g_E(h)\)為何？在此情況下，彈簧的振盪角頻率\(\tilde\omega_E\)為何(求出線性近似下的答案即可)？已知地球的半經為\(R_E\)。

\end{QTF}

果不其然，艾莉絲發現彈簧確實是以包柏預測的頻率振盪。

\begin{QTF}{0.3}{B}{5}
當振盪頻率\(\omega\)與地表測得的振盪頻率\(\tilde\omega_E\)相同時，太空站的半徑\(R\)為何？將答案以地球半徑\(R_E\)表示之。

\end{QTF}

艾莉絲被包柏的固執所刺激，而有一個新的想法，她想利用柯氏力(Coriolis force)來證明她的觀點。她從太空站底面爬上站內的一座高塔，由距離太空站底面為\(H\)的高度，讓一個質點落下。

在均勻轉動的座標系，太空人感受到一種假想力\(\vec{F}_C\)，稱之為柯氏力。當質量為\(m\)的物體，在一轉動座標系中以速度\(\vec v\)運動時，若座標系以固定的角速度\(\vec \omega_{ss}\)轉動，則作用於物體的柯氏力\(\vec F_C\)為

\begin{equation}
\vec F_C = 2m \vec v \times \vec \omega_{ss}\ .\end{equation}

當以純量表示時，你可以使用下式：

\begin{equation}
F_C = 2 m v \omega_{ss}  \sin \phi\ ,\end{equation}

其中\(\phi\)是物體的速度向量與轉動軸(或角速度向量)之間的夾角。柯氏力的方向和速度、轉動軸兩者都垂直，而此力的正負號可以用右手定則決定之。你在以下各題中，可以自行選擇一種方式來表達力。

\begin{QTF}{1.1}{B}{6}
計算當質點落在太空站底面瞬間的水平速度\(v_x\)與相對於塔底的位移\(d_x\)(即相對於塔底的垂直距離)。你可以假設塔高度\(H\)相對小，因此下落加速度可以視為定值。你也可以假設\(d_x \ll H\) 。

\end{QTF}

為了得到好的結果，艾莉絲決定從更高的塔上進行實驗。她很驚訝地發現，質點在太空站底面的落點就在塔底部(塔腳)，亦即\(d_x=0\)。

\begin{QTF}{1.3}{B}{7}
求能使\(d_x=0\)發生之塔的最小之高度。


\end{QTF}

為了使包柏相信，艾莉絲願意進行最後一次的嘗試。她想利用她的彈簧振盪器，以彰顯柯氏力的影響。為達此目的，她改變了原來的實驗裝置方式：她將彈簧連接到一個圓環，此圓環可在一水平直桿上沿\(x\)方向作無摩擦的滑動；彈簧本身則沿著\(y\)方向振盪 。直桿與太空站底面平行，且與太空站的旋轉軸垂直。因此， \(xy\) 平面與旋轉軸垂直，而\(y\)軸的方向筆直指向太空站的旋轉中心。

\vspace{0.5cm}\begin{minipage}{\textwidth}\centering

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{圖4: 實驗裝置}
\end{minipage}\vspace{0.5cm}

\begin{QTF}{1.7}{B}{8}
艾莉絲將質點從其平衡位置\(x=0\), \(y=0\)向下拉一距離\(d\) ，然後將它從靜止釋放(見圖 4)。

\begin{itemize}
\item 寫出\(x(t)\) 與 \(y(t)\)的代數表示式。你可假設\(\omega_{ss}d\) 是微小的，且忽略科氏力沿著y 軸的運動。

\item 以圖線繪出軌跡\((x(t),y(t))\)， 並將它的各種重要特徵標示出來，例如振幅。

\end{itemize}

\end{QTF}

艾莉絲和包柏仍持續爭執著！

\end{PR}
"""


answer_content = ur"""

\begin{PR}{Large Hadron Collider (10 points)}{10}

Please read the general instructions in the separate envelope before you start this problem.

In this task, the physics of the particle accelerator LHC (Large Hadron Collider) at CERN is discussed. The CERN is the largest particle physics laboratory. Its main goal is to get insights into the fundamental laws of nature. Two beams of particles are accelerated to high energies, guided around the accelerator ring by a strong magnetic field and then made to collide with each other. The resulting particles generated by collisions are observed with large detectors. Some parameters of the LHC can be found in table 1.


\vspace{0.5cm}\begin{center}\begin{tabular}{|ll|}\hline
\textbf{LHC ring} & \\\hline
Circumference of ring
 & \(26659 ~\text{m}\)\\\hline
Number of bunches per proton beam
 & \(2808\)
\\\hline
Number of protons per bunch
 & \(1.15 \times 10^{11}\)\\\hline
\textbf{Proton beams}
 & \\\hline
Nominal energy of protons
 & \(7.00 ~\text{TeV}\)\\\hline
Centre of mass energy (collision)
 & \(14.0 ~\text{TeV}\)\\\hline
\end{tabular}\end{center}\vspace{0.5cm}

\begin{center}
Table 1: Typical numerical values of relevant LHC parameters.
\end{center}

Particle physicists use convenient units for the energy, momentum and mass: The energy is measured in electron volts [\(\text{eV}\)]. By definition, \(1 ~\text{eV}\) is the amount of energy gained by a particle with elementary charge, e, moved through a potential difference of one volt (\(1~\text{eV}=1.602\cdot10^{-19}~\text{kg}\,\text{m}^2/\text{s}^2\)).

The momentum is measured in units of \(\text{eV}/c\) and the mass in units of \(\text{eV}/c^2\), where \(c\) is the speed of light in vacuum. Since \(1 ~\text{eV}\) is a very small quantity of energy, particle physicists often use \(\text{MeV}\) (\(1~\text{MeV}=10^6~\text{eV}\)), \(\text{GeV}\) (\(1~\text{GeV}=10^9~\text{eV}\)) or \(\text{TeV}\) (\(1~\text{TeV}=10^{12}~\text{eV}\)).

Part A deals with the acceleration of protons or electrons. Part B is concerned with the identification of particles produced in the collisions at CERN.


\PT{Part A. LHC accelerator (6 points)}{6}

\subsubsection*{Acceleration I:}

 Assume that the protons have been accelerated by a voltage \(V\) such that their velocity is very close to the speed of light and neglect any energy loss due to radiation or collisions with other particles.


\begin{QTF}{0.7}{A}{1}
Find an expression for the final velocity \(v\) of the protons as a function of the accelerating voltage \(V\), and fundamental constants.


\end{QTF}

A design for a future experiment at CERN plans to use the protons from the LHC and to collide them with electrons with an energy of \(60.0 ~\text{GeV}\).


\begin{QTF}{0.8}{A}{2}
For particles with high energy and low rest mass the relative deviation \(r = (c−v)/c\) of the final velocity \(v\) from the speed of light is very small. Find a suitable approximation for \(r\) and calculate \(r\) for electrons with an energy of \(60.0~\text{GeV}\).


\end{QTF}

We now return to the protons in the LHC. Assume that the beam pipe has a circular shape.


\begin{QTF}{1.0}{A}{3}
Derive an expression for the uniform magnetic flux density \(B\) necessary to keep the proton beam on a circular track. The expression should only contain the energy of the protons \(E\), the circumference \(L\), fundamental constants and numbers. You may use appropriate approximations if their effect is smaller than precision given by the least number of significant digits.

Calculate the magnetic flux density \(B\) for a proton energy of \(E = 7.00 ~\text{TeV}\).


\end{QTF}

\subsubsection*{Radiated Power:}

An accelerated charged particle radiates energy in the form of electromagnetic waves. The radiated power \(P_\text{rad}\) of a charged particle that circulates with a constant angular velocity depends only on its acceleration \(a\), its charge \(q\), the speed of light \(c\) and the permittivity of free space \(\varepsilon_0\).


\begin{QTF}{1.0}{A}{4}
Use a dimensional analysis to find an expression for the radiated power \(P_\text{rad}\).


\end{QTF}

The real formula for the radiated power contains a factor \(1/(6π)\); moreover, a full relativistic derivation gives an additional factor \(\gamma^4\), with \(\gamma = (1- v^2/c^2)^{-\frac{1}{2}}.\)


\begin{QTF}{1.0}{A}{5}
Calculate the total radiated power \( P_\text{tot}\) of the LHC for a proton energy of \(E = 7.00 ~\text{TeV}\) (Note table 1). You may use appropriate approximations.


\end{QTF}

At the LHC collider, protons at rest are accelerated by a linear accelerator of length \(d = 30.0 ~\text{m}\) through a potential difference of \(V = 500 ~\text{MV}\). Assume that the electrical field is homogeneous.


\begin{QTF}{1.5}{A}{6}
Determine the time \(T\) that the protons need to pass through this field.


\end{QTF}

\vspace{0.5cm}\begin{minipage}{\textwidth}\centering
\includegraphics[width=0.8\textwidth]{fig_q0_fi2}

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{Figure 1: Sketch of an accelerator module.}
\end{minipage}\vspace{0.5cm}

~\\ \clearpage

\PT{Part B. Particle Identification (4 points)}{4}

\subsubsection*{Time of flight:}

It is important to identify the high energetic particles that are generated in the collision to interpret the interaction process. A simple method is to measure the time (\(t\)) that a particle with known momentum needs to pass a length \(l\) in a so-called Time-of-Flight (ToF) detector. Typical particles which are identified in the detector together with their masses are listed in table 2.


\vspace{0.5cm}\begin{center}\begin{tabular}{|l|l|}\hline
\textbf{Particle}
 & \textbf{Mass }\(\mathrm{ [MeV / c^2] }\)\\\hline
Lambda
 & \(1116\)
\\\hline
Proton
 & \(938\)\\\hline
Kaon
 & \(498\)\\\hline
Pion
 & \(135\)
\\\hline
Electron
 & \(0.511\)
\\\hline
\end{tabular}\end{center}\vspace{0.5cm}

\begin{center}
Table 2: Particles and their masses.\end{center}

\vspace{0.5cm}\begin{minipage}{\textwidth}\centering
\includegraphics[width=0.9\textwidth]{fig_q0_fi3}

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{Figure 2: Schematic view of a time-of-flight detector.}
\end{minipage}\vspace{0.5cm}

\begin{QTF}{0.8}{B}{1}
Express the particle rest mass \(m\) as a function of the momentum \(p\), the flight length \( l\) and the flight time \(t\) assuming that the particles with elementary charge \(e\) travel with high velocity on straight tracks in the ToF detector and that it travels perpendicular to the two detection planes (see figure 2).


\end{QTF}

\begin{QTF}{0.7}{B}{2}
Calculate the length \(l\) of a ToF detector that allows to safely distinguish a kaon from a pion given both their momenta are measured to be \(1.00~\text{GeV/c}\). For a good separation it is required that the difference in the time-of-flight is larger than three times the time resolution of the detector. The typical resolution of a ToF detector is \(150 ~\text{ps} ~(1 ~\text{ps} = 10^{−12}~\text{s})\).


\end{QTF}

In the following, particles produced in a typical LHC detector are identified in a two stage detector consisting of a tracking detector and a ToF detector. Figure 3 shows the setup in the plane transverse and longitudinal to the proton beams. Both detectors are tubes surrounding the interaction region. The tracking detector measures the trajectory of a charged particle which passes through a magnetic field whose direction is parallel to the proton beams. The radius \(r\) of the trajectory allows to determine the transverse momentum \(\text{p}_\text{T}\) of the particle. Since the collision time is known the ToF detector only needs one tube to measure the flight time. This ToF tube is situated just after the tracking chamber. For this task you may assume that all particles created by the collision travel perpendicular to the proton beams, that means that the created particles have no longitudinal momentum.


\vspace{0.5cm}\begin{minipage}{\textwidth}\centering
\includegraphics[width=0.9\textwidth]{fig_q0_fi4}

\vspace{0.1cm}
\pbox[b]{0.9\textwidth}{(1) - ToF tube\\(2) - track\\(3) - collision point\\(4) - tracking detector\\ \\Figure 3 : Experimental setup for particle identification with a tracking chamber and a ToF detector. Both detectors are tubes surrounding the collision point in the middle. Left : transverse view perpendicular to the beamline, right : longitudinal view parallel to the beam line. The particle is travelling perpendicular to the beam line.}
\end{minipage}\vspace{0.5cm}

\begin{QTF}{1.7}{B}{3}
Express the particle mass as a function of the magnetic flux density \(B\), the radius \(R\) of the ToF tube, fundamental constants and the measured quantities: radius \(r\) of the track and time-of-flight \(t\).


\end{QTF}

We detected four different particles and want to identify them. The magnetic flux density in the tracking detector was \(B = 0.500 ~\text{T}\). The radius \(R\) of the ToF tube was \(3.70 ~\text{m}\). Here are the measurements (\(1 ~\text{ns}=10^{−9}~\text{s}\)):


\vspace{0.5cm}\begin{center}\begin{tabular}{|l|l|l|}\hline
\emph{Particle} & \emph{Radius} \(r\) \(\text{[m]}\) & \emph{Time of flight \(t\) \(\text{[ns]}\)}\\\hline
A & \(5.10\) & \(20\)\\\hline
B & \(2.91\) & \(14\)\\\hline
C & \(6.06\) & \(18\)\\\hline
D & \(2.32\) & \(25\)\\\hline
\end{tabular}\end{center}\vspace{0.5cm}

\begin{QTF}{0.8}{B}{4}
Identify the four particles by calculating their mass.


\end{QTF}

\end{PR}
"""


def _compile_tex(body, ext_resources):
    try:
        return pdf.compile_tex(body, ext_resources)
    except pdf.TexCompileException as err:
        print(err)
        print(err.log)
        raise


def compile_cover():
    cover = {'student': student, 'exam': exam, 'question': question, 'place': 'M439'}
    body = render_to_string('ipho_exam/tex/exam_cover.tex', RequestContext(HttpRequest(), cover)).encode("utf-8")
    question_pdf = _compile_tex(body, [])
    bgenerator = iphocode.QuestionBarcodeGen(exam, question, student, qcode='C')
    page = pdf.add_barcode(question_pdf, bgenerator)
    with open('test_cover.pdf', 'wb') as pdf_file:
        pdf_file.write(page)



def compile_question(qml_trans, pdf_name='test_question'):
    ext_resources = []
    ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
    context = {
                'polyglossia' : language.polyglossia,
                'polyglossia_options' : language.polyglossia_options,
                'font'        : fonts.ipho[language.font],
                'extraheader' : language.extraheader,
                'lang_name'   : u'{} ({})'.format(language.name, 'Country'),
                'exam_name'   : u'{}'.format(exam.name),
                'code'        : u'{}{}'.format(question.code, question.position),
                'title'       : u'{} - {}'.format(exam.name, question.name),
                'is_answer'   : True,
                'document'    : qml_trans,
              }
    body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
    question_pdf = _compile_tex(body, ext_resources)
    bgenerator = iphocode.QuestionBarcodeGen(exam, question, student)
    page = pdf.add_barcode(question_pdf, bgenerator)
    with open('{}.pdf'.format(pdf_name), 'wb') as pdf_file:
        pdf_file.write(page)


def compile_blank():
    pages = 3
    context = {
                'polyglossia' : 'english',
                'polyglossia_options' : '',
                'font'        : fonts.ipho['notosans'],
                'extraheader' : '',
                'exam_name'   : u'{}'.format(exam.name),
                'code'        : u'W2',
                'title'       : u'{} - {}'.format(exam.name, question.name),
                'is_answer'   : True,
                'pages'       : range(pages),
              }
    body = render_to_string('ipho_exam/tex/exam_blank.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
    question_pdf = _compile_tex(body, [
        tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')
    ])
    bgenerator = iphocode.QuestionBarcodeGen(exam, question, student, qcode='W')
    page = pdf.add_barcode(question_pdf, bgenerator)
    with open('test_blank.pdf', 'wb') as pdf_file:
        pdf_file.write(page)


def compile_graph():
    pages = 3
    context = {
                'polyglossia' : 'english',
                'polyglossia_options' : '',
                'font'        : fonts.ipho['notosans'],
                'extraheader' : '',
                'exam_name'   : u'{}'.format(exam.name),
                'code'        : u'W2',
                'title'       : u'{} - {}'.format(exam.name, question.name),
                'is_answer'   : True,
                'pages'       : range(pages),
              }
    body = render_to_string('ipho_exam/tex/exam_graph.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
    question_pdf = _compile_tex(body, [
        tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')
    ])
    bgenerator = iphocode.QuestionBarcodeGen(exam, question, student, qcode='W')
    page = pdf.add_barcode(question_pdf, bgenerator)
    with open('test_graph.pdf', 'wb') as pdf_file:
        pdf_file.write(page)

if __name__ == '__main__':
    compile_cover()
    compile_question(doc_content)
    compile_blank()
    compile_question(answer_content, pdf_name='test_answer')
    compile_graph()
