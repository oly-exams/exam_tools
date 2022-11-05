# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

from django.shortcuts import render
from django.template import RequestContext
from django.templatetags.static import static


def index(request):
    return render(request, "example_exam/index.html", context=RequestContext(request))


def view_exam(request, display_tpl="show"):

    base_template = (
        "base_fullexam.html" if display_tpl == "show" else "base_ckeditor.html"
    )
    context = RequestContext(request)
    context["base_template"] = base_template
    return render(
        request,
        "example_exam/theo_2011_Q1.html",
        context=context,
    )


def view(request):
    return view_exam(request, display_tpl="show")


def edit(request):
    return view_exam(request, display_tpl="edit")


def inline_edit(request):
    title = "Ein Drei-Körper-Problem und LISA"

    parts = []

    parts.append(
        """
    <div class="figure">
        <img src="{}" /><br />
        ABBILDUNG 1: Koplanare Umlaufbahnen der drei Körper.
        ("Koplanar": in der gleichen Ebene liegend)
    </div>
    """.format(
            static("exam/img/fig1.svg")
        )
    )

    parts.append(
        """ <p>1.1	Zwei gravitativ wechselwirkende Massen
    $m$ und $M$ bewegen sich auf kreisförmigen Umlaufbahnen mit den
    jeweiligen Radien $r$ und $R$ um ihren gemeinsamen Schwerpunkt.
    Bestimme die Winkelgeschwindigkeit $w_0$ der Verbindungslinie
    zwischen $M$ und $m$ als Funktion von $R,r,M,m$ und der universellen
    Gravitationskonstanten $G$.</p> """
    )

    parts.append(
        """ <p>1.2	Ein dritter Körper mit vernachlässigbarer
    Masse $m$ befinde sich auf einer koplanaren kreisförmigen Umlaufbahn
    um den gleichen Schwerpunkt, so dass  stationär relativ zu $M$ und
    $m$ bleibt, wie Abbildung 1 zeigt. Nimm an, dass die Masse $m$ sich
    nicht auf einer Linie mit $M$ und $m$ befindet. Bestimme Ausdrücke
    für die folgenden Parameter als Funktion von $R$ und $r$: <ul>
    <li>Entfernung zwischen $m$ und $M$.</li> <li>Entfernung zwischen
    $m$ und $m$.</li> <li>Entfernung zwischen $m$ und dem
    Schwerpunkt.</li> </ul> </p> """
    )

    parts.append(
        r""" <p>1.3	Betrachte den Fall $M=m$. Wenn die Masse
    $m$ geringfügig in radialer Richtung (entlang der Linie durch $O$
    und $m$) ausgelenkt wird, oszilliert sie um ihre Gleichgewichtslage.
    Berechne die Winkelfrequenz dieser Schwingung als Funktion von
    $\omega_0$. Nimm dabei an, dass der Drehimpuls von $m$ erhalten
    bleibt.</p> """
    )

    parts.append(
        """ <p> Die Laser-Interferometrie-Weltraumantenne
    ("Laser Interferometry Space Antenna", LISA) ist eine Gruppe von
    drei identischen Weltraumsonden, die niederfrequente
    Gravitationswellen detektieren soll. Jede der drei Sonden befindet
    sich an einer Ecke eines gleichseitigen Dreiecks, wie man auf den
    Abbildungen 2 und 3 sehen kann. Die Seiten bzw. "Arme" dieser
    Dreiecke sind ungefähr 5.0 Millionen Kilometer lang. Die
    LISA-Konstellation befindet sich in einer erdähnlichen Umlauf-bahn
    um die Sonne, folgt der Erde aber 20° nach. Jede dieser Sonden
    bewegt sich auf einer eigenen, leicht geneigten Umlaufbahn um die
    Sonne. Die drei Sonden scheinen damit effektiv insgesamt in einem
    Jahr eine ganze Umdrehung um ihren gemeinsamen Schwerpunkt zu
    vollführen. </p> """
    )

    parts.append(
        """ <p>Die Sonden tauschen ständig Lasersignale
    untereinander aus. Sie detektieren Gravitationswellen mittels
    Interferometrie anhand von winzigen Änderungen in der Armlänge. Eine
    Kollision massiver Objekte in einer nahen Galaxie, etwa von zwei
    schwarzen Löchern, wäre ein Beispiel einer Quelle von
    Gravitationswellen.</p> """
    )

    parts.append(
        """ <div class="figure"> <img src="{}" /><br /> ABBILDUNG 2: Bild der
    LISA-Umlaufbahn. (Sun: Sonne, Earth: Erde, AU: Astronomische Einheit
    (AE, mittlerer Abstand Erde-Sonne)) Die drei Sonden kreisen um ihren
    gemeinsamen Schwerpunkt mit einer Umlaufdauer von einem Jahr.
    Anfangs befinden sie sich   hinter der Erde. (Skizze aus D.A.
    Shaddock, "An Overview of the Laser Interferometer Space Antenna",
    Publications of the Astronomical Society of Australia, 2009, 26,
    S.128-132.). </div> """.format(
            static("exam/img/fig2.svg")
        )
    )

    parts.append(
        """ <div class="figure"> <img src="{}" /><br /> ABBILDUNG 3: Vergrösserte Sicht auf
    die drei Sonden, die der Erde nachfolgen. A, B und C sind die drei
    Sonden an den Ecken eines gleichseitigen Dreiecks. </div> """.format(
            static("exam/img/fig3.svg")
        )
    )

    parts.append(
        """ <p>1.4	Betrachte die Bewegung der Sonden in der
    Ebene in der sie sich befinden. Berechne die Relativgeschwindigkeit
    jeweils zweier Sonden zueinander.</p> """
    )

    return render(request, "base_exam.html", {"exam_title": title, "exam_parts": parts})


def mathquill(request):
    return render(request, "test_mathquill.html", context=RequestContext(request))


def mathquill_toolbar(request):
    return render(
        request, "test_mathquill_toolbar.html", context=RequestContext(request)
    )
