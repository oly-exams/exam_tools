\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ipho2016}[2016/02/06 Template for Exam Tools problems]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions

\LoadClass[a4paper,9pt]{article}


% Packages

% PDF search & cut'n'paste
\RequirePackage{cmap}
% PDF metadata
\RequirePackage[pdfauthor={Exam Tools},
                pdfproducer={XeLateX},
                pdfcreator={Xelatex}]{hyperref}

% Page options
\RequirePackage[headheight=5cm]{geometry}  % the headheight parameter sets how much vertical space the header can accomodate
%\setlength{\headheight}{2.5cm}
\geometry{left=2cm}
\geometry{right=2cm}
\geometry{top=5.5cm}  % change this to change the header height (i.e. if the QR code size is changed)
\geometry{bottom=2cm}

%Paragraph spacing
\RequirePackage{parskip}

%Pbox (for Figure & Table captions)
\RequirePackage{pbox}

% Font settings
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
%\setmainfont{Arial Unicode MS} %Calibri
\setotherlanguage{english}
\newfontfamily\englishfont[ Path = {{ STATIC_PATH }}/noto/,BoldFont=NotoSans-Bold.ttf, ItalicFont=NotoSans-Italic.ttf, BoldItalicFont=NotoSans-BoldItalic.ttf, ]{NotoSans-Regular.ttf}
% Usage:
% Start other language with \begin{English}, or \textenglish

% Headers
\RequirePackage{fancyhdr}
\renewcommand{\headrulewidth}{2pt}
%\fancyheadoffset{1cm} % make heading go out horizontally
\pagestyle{fancy}

% Math
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amsfonts}
\RequirePackage[]{unicode-math}
%\setmathfont{XITS Math}

% Others
\RequirePackage{framed}
\RequirePackage{xcolor}
\RequirePackage{siunitx}

% Fix fontenc problem with hbar display that appears for e.g. for CJK fonts (necessary for Texlive 2015, but not for e.g. 2018)
\AtBeginDocument{%
  \let\hbar\relax
  \DeclareRobustCommand{\hbar}{\text{\normalfont\fontfamily{lmr}\itshape\symbol{295}}}%
}

%Definitions
\definecolor{color1}{rgb}{0,0,.7}

%Commands

\setlength{\emergencystretch}{3em}

% Table spacing
\renewcommand{\arraystretch}{1.3}

%Fix font in units
\newfontfamily\mathunits{latinmodern-math.otf}
\let\oldtext\text
\renewcommand{\text}[1]{\oldtext{\mathunits #1}}

%Problem (QMLquestion)
\newenvironment{PR}[2]
      {% templatetag openbrace %}{\noindent\fontsize{16pt}{14pt}\fontshape{bf}\selectfont\textcolor{color1}{\textbf{#1}}}}



%Part
\newcommand{\PT}[2]{\vspace{0.3cm}\noindent
    { \hspace*{-3pt}\fontsize{11pt}{11pt}\selectfont\textcolor{color1}{\textbf{#1}}}\nopagebreak}
    {\vspace{0.1cm}}\nopagebreak



%Question -- no longer used
\newcommand{\QT}[3]{\vspace{0.2cm}\noindent{\textbf\Alph#2\arabic#3.~(#1 \if#11{pt}\else{pts}\fi)}}


%Question (QMLsubquestion)
\newenvironment{QTF}[3]
{\def\QTFpoints{#1} %\vspace{0.5em}
\begin{framed}
   \noindent
   \parbox[t]{.1\textwidth}{
   \hspace{1em}
    % \noindent\textbf \Alph{ptnum}\arabic{qtnum2}
    \begin{english}\noindent\textbf{#2.#3}\end{english}
 }
 \begin{minipage}[t]{.79\textwidth}}
{
\end{minipage}
\parbox{.1\textwidth}{
    \hspace{1em} \begin{english} \QTFpoints pt \end{english}
}
% \vspace{0.5em}
\end{framed}
}

% Subanswer (QMLsubanswer)
\newenvironment{QSA}[4]
{
    \def\QSApoints{#1} %\vspace{0.5em}
    \renewcommand{\arraystretch}{2.}
    \begin{framed}\noindent\begin{minipage}[t][#4][t]{\textwidth}
    {\noindent\textbf{ \begin{english} #2.#3 $(\QSApoints ~\text{pt})$ \end{english}}}

}
{
    \end{minipage}\end{framed}
}

% Subanswer continuation (QMLsubanswercontinuation)
\newenvironment{QSAC}[3]
{
    \renewcommand{\arraystretch}{2.}
    \begin{framed}\noindent\begin{minipage}[t][#3][t]{\textwidth}
    {\noindent\textbf{ \begin{english} #1.#2 (cont.) \end{english}}}

}
{
    \end{minipage}\end{framed}
}

% Box (QMLbox)
\newenvironment{QBO}[1]
{
    \renewcommand{\arraystretch}{2.}
    \begin{framed}\noindent\begin{minipage}[t][#1][t]{\textwidth}

}
{
    \end{minipage}\end{framed}
}

% \newenvironment{QTF}[1]
% {\def\QTFpoints{#1}
% \tabularx{\textwidth}{|l|p{.8\textwidth}|r|} \hline
%    \noindent
%     % \noindent\textbf \Alph{ptnum}\arabic{qtnum2}
%     \begin{english}\noindent\textbf \Alph{ptnum}.\arabic{qtnum2}\end{english}
%     &
%  }
% { & \QTFpoints pt \tabularnewline
% \hline
% \endtabularx
% \addtocounter{qtnum2}{1}}




% \newcommand{\unit}[1]{\,\mathrm{#1}}
% \newcommand{\e}[1]{\cdot 10^{#1}}
% \RequirePackage[ngerman=ngerman-x-latest]{hyphsubst}
