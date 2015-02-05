# -*- coding: cp1252 -*-
import re
import requests
import cgi
import xml.etree.ElementTree as ET

# TODO: start using del more
# TODO: get rid of duplicated code, especially in the "bestScore" technique

artistList = set()

def addToArtistList(artist):
    artistList.add(artist.lower().strip())

"""
Returns a tuple of (artist, title) or (None, None)
"""
def parse(raw, useLastFM):
    if raw.find(" ") == -1:
        # TODO: Case we ~probably~ downloaded from soundcloud

        # Do soundcloud stuff, if it didnt work then
        raw = raw.replace("-", " ")

    cleanRaw, brackets = sanitize(raw)
    artist, title = tryGetTags(cleanRaw, useLastFM)

    if artist is None:
         return None, None
    else:
        # Add to storage
        addToArtistList(artist)
        
        brackets.insert(0, title)
        return (artist.strip(), " ".join(brackets).strip())

"""
Returns tuple of
(cleaned string, [remix1, remix2, ...])

Functions:
- remove useless brackets
- replace _ with space
- replace ~ with -

"""
def sanitize(raw):
    # Might make upto the user
    badNames = ["official", "audio", "video",
                "lyrics", "video", "hd", "hq", "song",
                "mp3", "128", "tv", "original", "youtube",
                "new 2014", "new 2015", "2014 new", "2015 new", "music", 
                "2014", "2015", "2013", "explicit"]
    brackets = []
    out = []

    # TODO: Maybe make more specific because atm it could match things we dont need to match
    raw = re.sub(r"\'(.+)\'", r"\1", raw)
    raw = re.sub(r"\"(.+)\"", r"\1", raw)
    raw = re.sub(r"(_+\d_*| \d+\.+)", " ", raw)
    # Substitutions
    for i, j in {"~":"-", "_":" ", "[":"(", "]":")", u"\u2014":"-"}.iteritems():
        raw = raw.replace(i, j)

    # do the bracket subs
    bOpen = 0
    bClose = 0
    while True:
        bOpen = raw.find("(", bClose)
        if bOpen == -1:
            out.append(raw[bClose:])
            break

        # Seeked up, now add it
        out.extend([raw[bClose:bOpen]," "])

        # Need to include the bracket
        bClose = raw.find(")", bClose) + 1
        if bClose == 0:
            bClose = bOpen + 1
            out.append("(")
            continue

        bracketed = raw[bOpen:bClose] # between, note lowercase
        lowerBrack = bracketed.lower()
        bad = False
        for badName in badNames:
            if lowerBrack.find(badName) != -1:
                bad = True
                break
        if not bad:
            brackets.append(bracketed)

    # Little bit more processing
    out = re.sub("\s+", " ", "".join(out)).strip().split(" ")

    # Might eliminate
    remove = []
    for token in out:
        tLower = token.lower()
        if tLower in badNames:
            remove.append(token)
    
    for rm in remove:
        out.remove(rm)

    # Seek up past the qaulifier
    return (" ".join(out), brackets)

"""
Returns the number of hits if there is a match, and -1 otherwise
"""
def queryLastFM(string):
    try:
        print "trying " + string
        # Just for debugging but might not work with some unicode chars
    except:
        pass
    # TODO: Careful about safety of string
    params = {
        "method":"artist.search",
        "artist":cgi.escape(string, True),
        "limit":"10",
        "api_key":"f18fa52ed0c0850108c6d74a453b3621",
        "api_secret":"5a76a480a66768bfbd1e6d7ed4cdecd0"
    }
    # TODO: FIX
    try:
        tree = ET.fromstring(
            requests.get("http://ws.audioscrobbler.com/2.0/", params=params).content)
    except:
        print "Bad Query"
        return -1
    
    # No matches?
    try:
        artists = tree.find("results").find("artistmatches").findall("artist")
    except:
        return -1

    if not artists:
        # Empty list
        return -1

    for artist in artists:
        if string.lower().strip() == artist.find("name").text.lower().strip():
            try:
                score = int(artist.find("listeners").text)
            except AttributeError:
                # No listeners?
                continue
            if score > 10:
                return score
    del tree
    return -1

"""
returns the number of listeners if theres a match
"""
def artistScore(string, useLastFM):
    # Check if inside artistList, in which case we give an aribtrarily large score
    if string.lower().strip() in artistList:
        return 50000

    # Now make some guesses
    res = -1
    reg = re.compile(r"\s*(?:and|x+|(?:ft|feat)\.?|,|&)\s+", flags=re.I)
    if reg.search(string) is not None:
        print "Here"
        for token in reg.split(string):
            queryRes = queryLastFM(token)
            if queryRes != -1: # in which case we'll keep looking
                res += queryRes
    if res != -1:
        return res
    
    if not useLastFM:
        return -1
    
    return queryLastFM(string)

"""
Takes a sanitized string and tries to find the artist and title
(artist, title)
or None, None on failure
"""
def tryGetTags(string, useLastFM):
    # Tricky thing with ft., if its trailing then we should insta prepare it for output
    ftpos = re.search(r" (?:ft|feat)\.?[^-]+$", string, flags=re.I)
    feat = ""
    if ftpos:
        feat = string[ftpos.start():]
        string = string[:ftpos.start()]

    delims = [r" -+ ", r" -+", r"-+ ", r" by\.? ",
              r"/+", r"-+", r" [^\w,&]+ "]
    for delim in delims:
        #try to split it through each delim format
        potential = {}
        bestScore = -1

        tokens = re.split(delim, string, flags=re.I)
        if len(tokens) == 1:
            # No point if its just the same string
            continue

        for token in tokens:
            score = artistScore(token, useLastFM)
            if score != -1 and score > bestScore:
                bestScore = score
                potential[score] = token
        if bestScore != -1:
            tokens.remove(potential[bestScore])
            return (potential[bestScore] + feat, " ".join(tokens))

    # Not worth the effort
    if not useLastFM:
        return None, None

    # we've failed, time to do it the hard way
    string = re.sub("\s{2,}"," ",string.replace(",", " "))
    # TODO: optimize

    tokens = string.split(" ")
    if len(tokens) == 1:
        return None, None

    bestScore = -1
    potential = {}

    other = []
    while tokens:
        qStr = " ".join(tokens)
        res = queryLastFM(qStr)
        if res != -1 and res > bestScore:
            potential[res] = (qStr + feat, " ".join(other))
            bestScore = res
        other.insert(0, tokens.pop())

    # Reverse walkthrough?
    while other:
        qStr = " ".join(other)
        res = queryLastFM(qStr)
        if res != -1 and res > bestScore:
            potential[res] = (qStr + feat, " ".join(tokens))
            bestScore = res
        tokens.append(other.pop(0))

    if bestScore == -1:
        return None, None # just to simplify fxn calls
    else:
        return potential[bestScore]


        
