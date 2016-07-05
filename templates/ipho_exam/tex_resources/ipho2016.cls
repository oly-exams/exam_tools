\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ipho2016}[2016/02/06 Template for IPhO 2016 problems]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions

\LoadClass[a4paper,9pt]{article}


% Packages

% PDF search & cut'n'paste
\RequirePackage{cmap}
% PDF metadata
\RequirePackage[pdfauthor={IPhO 2016},
                pdfproducer={XeLateX},
                pdfcreator={Xelatex}]{hyperref}

% Page options
\RequirePackage{geometry}
\setlength{\headheight}{2.5cm}
\geometry{left=2cm}
\geometry{right=2cm}
\geometry{top=5.5cm}
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
\fancyhf[HL]{\includegraphics[width=2cm]{% templatetag openbrace %}{{ STATIC_PATH }}/ipho16_small_green.pdf} }

% Math
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amsfonts}
\RequirePackage[]{unicode-math}
%\setmathfont{XITS Math}

% Others
\RequirePackage{framed}
\RequirePackage{xcolor}



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
      {% templatetag openbrace %}{\noindent\fontsize{16pt}{14pt}\fontshape{bf}\selectfont\textcolor{color1}{\textbf{#1 \textenglish{\fontshape{it}\selectfont(#2 points)}}}}}



%Part
\newcommand{\PT}[2]{\vspace{0.3cm}\noindent
    { \hspace*{-3pt}\fontsize{11pt}{11pt}\selectfont\textcolor{color1}{\textbf{#1 \textenglish{(#2 points)}}}}}
    {\vspace{0.1cm}}



%Question -- no longer used
\newcommand{\QT}[3]{\vspace{0.2cm}\noindent{\bf\Alph#2\arabic#3.~(#1 \if#11{pt}\else{pts}\fi)}}


%Question (QMLsubquestion)
\newenvironment{QTF}[3]
{\def\QTFpoints{#1} %\vspace{0.5em}
\begin{framed}
   \noindent
   \parbox[t]{.1\textwidth}{
   \hspace{1em}
    % \noindent\bf \Alph{ptnum}\arabic{qtnum2}
    \begin{english}\noindent\bf #2.#3\end{english}
 }
 \begin{minipage}[t]{.79\textwidth}}
{
\end{minipage}
\parbox{.1\textwidth}{
  \hspace{1em} \QTFpoints pt
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
    \begin{english}\noindent\bf #2.#3 (\QSApoints ~pt) \end{english}
    
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
%     % \noindent\bf \Alph{ptnum}\arabic{qtnum2}
%     \begin{english}\noindent\bf \Alph{ptnum}.\arabic{qtnum2}\end{english}
%     &
%  }
% { & \QTFpoints pt \tabularnewline
% \hline
% \endtabularx
% \addtocounter{qtnum2}{1}}




% \newcommand{\unit}[1]{\,\mathrm{#1}}
% \newcommand{\e}[1]{\cdot 10^{#1}}
% \RequirePackage[ngerman=ngerman-x-latest]{hyphsubst}
