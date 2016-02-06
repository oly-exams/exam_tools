\NeedsTeXFormat{LaTeX2e} 
\ProvidesClass{ipho2016}[2016/02/06 Template for IPhO 2016 problems]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions

\LoadClass[a4paper,11pt]{article}

\addtolength{\hoffset}{-1.2cm}
\addtolength{\textwidth}{2.8cm}
\addtolength{\voffset}{-1.7cm}
\addtolength{\textheight}{4.0cm}


% Packages

% PDF search & cut'n'paste
\RequirePackage{cmap}
% PDF metadata
\RequirePackage[pdfauthor={IPhO 2016},
                pdfproducer={XeLateX},
                pdfcreator={Xelatex}]{hyperref}

% Page options
% \RequirePackage{geometry}
% \geometry{left=2.5cm}
% \geometry{right=2.5cm}
% \geometry{top=1cm}
% \geometry{bottom=2cm}

% Font settings
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
\setmainfont{Arial Unicode MS} %Calibri
% Usage:
% Start other language with \begin{English}, or \textenglish

% Math
\RequirePackage{amsmath}
\RequirePackage[]{unicode-math}
%\setmathfont{XITS Math}

% Others
\RequirePackage{framed}
\RequirePackage{xcolor}



%Definitions
\newcounter{qtnum}
\newcounter{prnum}
\newcounter{ptnum}
\newcounter{epsnum}
\setcounter{prnum}{1}
\setcounter{epsnum}{0}
\definecolor{color1}{rgb}{0,0,.7}


\newcounter{qtnum2}
\setcounter{qtnum2}{1}

%Commands

%Problem
\newenvironment{PR}[2]
      {\ifnum\value{prnum}<2{\setcounter{epsnum}0}\fi{\addtocounter{epsnum}{1}}
%        \begin{framed}
      {\noindent\sf\bfseries\fontsize{12pt}{16pt}\fontencoding{T1}\selectfont 
      \textcolor{color1}{Problem \arabic{prnum} :  #1 {\fontshape{it}\selectfont(#2 points)}}}}
      {
%        \end{framed}
      \addtocounter{prnum}{1}\setcounter{ptnum}{0}\setcounter{qtnum}{0}}



%Part
\newcommand{\PT}[2]{\vspace{0.3cm}\noindent\addtocounter{ptnum}{1}\setcounter{qtnum}{0}\setcounter{qtnum2}{1}
	{\sf\fontseries{b}\selectfont \hspace*{-3pt}\textcolor{color1}{Part \Alph{ptnum}.~#1 {\fontshape{it}\selectfont(#2 points)}}}
	{\vspace{0.1cm}}
	}

	
%Question
\newcommand{\QT}[1]{\vspace{0.2cm}\noindent\addtocounter{qtnum}{1}{\bf\Alph{ptnum}\arabic{qtnum}.~(#1 \if#11{pt}\else{pts}\fi)}}


\newenvironment{QTF}[1]
      {\begin{framed}
      {\noindent\bf \Alph{ptnum}\arabic{qtnum2} (#1 pt)}}
      {
        \end{framed}
      \addtocounter{qtnum2}{1}}


\newcommand\subquestion[2]{
\vspace{0.5em}
\noindent
  \framebox[\textwidth]{
    \vspace{0.5em}
    \parbox[t]{.1\textwidth}{
      \hspace{1em}
      X.Y
    }
    \parbox[t]{.8\textwidth}{
      #2 % content here
    }
    \parbox{.1\textwidth}{
      \flushright
      #1 pt
      \hspace{1em}
    }
    \vspace{0.5em}
  }
\vspace{0.5em}
}

% \newcommand{\unit}[1]{\,\mathrm{#1}}
% \newcommand{\e}[1]{\cdot 10^{#1}}
% \RequirePackage[ngerman=ngerman-x-latest]{hyphsubst}
