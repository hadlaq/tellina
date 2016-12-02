from explainshell import matcher, errors, util, store, config

def explaincommand(command, store):
    matcher_ = matcher.matcher(command, store)
    groups = matcher_.match()
    expansions = matcher_.expansions
    shellgroup = groups[0]
    commandgroups = groups[1:]
    matches = []

    # save a mapping between the help text to its assigned id,
    # we're going to reuse ids that have the same text
    texttoid = {}

    # remember where each assigned id has started in the source,
    # we're going to use it later on to sort the help text by start
    # position
    idstartpos = {}

    l = []
    for m in shellgroup.results:
        commandclass = shellgroup.name
        helpclass = 'help-%d' % len(texttoid)
        text = m.text
        if text:
            text = text#.decode('utf-8')
            helpclass = texttoid.setdefault(text, helpclass)
        else:
            # unknowns in the shell group are possible when our parser left
            # an unparsed remainder, see matcher._markunparsedunknown
            commandclass += ' unknown'
            helpclass = ''
        if helpclass:
            idstartpos.setdefault(helpclass, m.start)

        d = _makematch(m.start, m.end, m.match, commandclass, helpclass)
        formatmatch(d, m, expansions)

        l.append(d)
    matches.append(l)

    for commandgroup in commandgroups:
        l = []
        for m in commandgroup.results:
            commandclass = commandgroup.name
            helpclass = 'help-%d' % len(texttoid)
            text = m.text
            if text:
                text = text#.decode('utf-8')
                helpclass = texttoid.setdefault(text, helpclass)
            else:
                commandclass += ' unknown'
                helpclass = ''
            if helpclass:
                idstartpos.setdefault(helpclass, m.start)

            d = _makematch(m.start, m.end, m.match, commandclass, helpclass)
            formatmatch(d, m, expansions)

            l.append(d)

        d = l[0]
        d['commandclass'] += ' simplecommandstart'
        if commandgroup.manpage:
            d['name'] = commandgroup.manpage.name
            d['section'] = commandgroup.manpage.section
            if '.' not in d['match']:
                d['match'] = '%s(%s)' % (d['match'], d['section'])
            d['suggestions'] = commandgroup.suggestions
            d['source'] = commandgroup.manpage.source[:-5]
        matches.append(l)

    matches = list(itertools.chain.from_iterable(matches))
    helpers.suggestions(matches, command)

    # _checkoverlaps(matcher_.s, matches)
    matches.sort(key=lambda d: d['start'])

    it = util.peekable(iter(matches))
    while it.hasnext():
        m = it.next()
        spaces = 0
        if it.hasnext():
            spaces = it.peek()['start'] - m['end']
        m['spaces'] = ' ' * spaces

    helptext = sorted(texttoid.iteritems(), key=lambda k, v: idstartpos[v])

    return matches, helptext
