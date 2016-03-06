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
%\setmainfont{Arial Unicode MS} %Calibri
\setotherlanguage{english}
\newfontfamily\englishfont{Noto Sans}
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
\definecolor{color1}{rgb}{0,0,.7}
\newcounter{qtnum}
\newcounter{prnum}
\newcounter{ptnum}
\newcounter{epsnum}
\setcounter{prnum}{1}
\setcounter{epsnum}{0}


\newcounter{qtnum2}
\setcounter{qtnum2}{1}

%Commands

%Problem
\newenvironment{PR}[2]
      {\ifnum\value{prnum}<2{\setcounter{epsnum}0}\fi{\addtocounter{epsnum}{1}}
      {\noindent\fontsize{18pt}{16pt}\fontshape{bf}
      \textcolor{color1}{\textbf{#1 \textenglish{\fontshape{it}(#2 points)}}}}}
      {
      \addtocounter{prnum}{1}\setcounter{ptnum}{0}\setcounter{qtnum}{0}}



%Part
\newcommand{\PT}[2]{\vspace{0.3cm}\noindent\addtocounter{ptnum}{1}\setcounter{qtnum}{0}\setcounter{qtnum2}{1}
    { \hspace*{-3pt}\fontsize{12pt}{14pt}\textcolor{color1}{\textbf{\textenglish{Part \Alph{ptnum}.}~#1 \textenglish{(#2 points)}}}}
    {\vspace{0.1cm}}
    }


%Question
\newcommand{\QT}[1]{\vspace{0.2cm}\noindent\addtocounter{qtnum}{1}{\bf\Alph{ptnum}\arabic{qtnum}.~(#1 \if#11{pt}\else{pts}\fi)}}


\newenvironment{QTF}[1]
{\def\QTFpoints{#1} %\vspace{0.5em}
\begin{framed}
   \noindent
   \parbox[t]{.1\textwidth}{
   \hspace{1em}
    % \noindent\bf \Alph{ptnum}\arabic{qtnum2}
    \begin{english}\noindent\bf \Alph{ptnum}.\arabic{qtnum2}\end{english}
 }
 \begin{minipage}[t]{.79\textwidth}}
{
\end{minipage}
\parbox{.1\textwidth}{
  \hspace{1em} \QTFpoints pt
}
% \vspace{0.5em}
\end{framed}
\addtocounter{qtnum2}{1}}


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
