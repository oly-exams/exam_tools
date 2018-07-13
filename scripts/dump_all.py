#!/usr/bin/env python

import sys
import os
import os.path

if __name__ == "__main__":
    output_dir = sys.argv[1]
    try:
        os.makedirs(output_dir)
    except:
        pass

    fn = os.path.join(output_dir, '999_fulldump.json')
    os.system('python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --exclude auth.permission --exclude contenttypes --exclude admin --exclude djcelery --exclude sessions --exclude ipho_core.PushSubscription --exclude ipho_exam.Figure --exclude ipho_exam.CompiledFigure --exclude ipho_exam.RawFigure > "{}"'.format(fn))

    os.system('python scripts/export_figures.py "{}"'.format(output_dir))
