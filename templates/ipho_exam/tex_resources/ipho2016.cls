\NeedsTeXFormat{LaTeX2e} 
\ProvidesClass{ipho2016}[2016/01/02 Template for IPhO 2016 problems]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions

\LoadClass[a4paper,11pt]{article}

\addtolength{\hoffset}{-1.2cm}
\addtolength{\textwidth}{2.8cm}
\addtolength{\voffset}{-1.7cm}
\addtolength{\textheight}{4.0cm}


% Packages
\RequirePackage[english]{babel}
\RequirePackage{amsmath, amsfonts, amssymb}
\RequirePackage{enumerate}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage{sistyle}
\RequirePackage[colorlinks=true, linkcolor=black, urlcolor=blue]{hyperref}
\RequirePackage{caption}
\RequirePackage{wrapfig}
\RequirePackage{multicol}
\RequirePackage[usenames,dvipsnames]{xcolor}
\RequirePackage{framed}


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



% \newcommand{\unit}[1]{\,\mathrm{#1}}
% \newcommand{\e}[1]{\cdot 10^{#1}}
% \RequirePackage[ngerman=ngerman-x-latest]{hyphsubst}

