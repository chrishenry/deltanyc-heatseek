def clean_addresses(table, column):
    """ Returns a SQL statement cleaning an address column.
        |table| and |column| are both strings.
    """
    # One line missing:
    #    UPDATE {table} SET {column} = array_to_string(regexp_matches('(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '', {column} ) WHERE {column} ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    # No idea where regexp_matches is defined? Looks like it's a Postgresql command?
    return '''
    UPDATE {table} SET {column} = preg_replace( '/ AVE$|-AVE$| -AVE$/', ' AVENUE', {column} );
    UPDATE {table} SET {column} = preg_replace( '/\./', '', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ LA$/', ' LANE', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ LN$/', ' LANE', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ PL$/', ' PLACE', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ ST$| STR$/', ' {column}', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ RD$/', ' ROAD', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ PKWY$/', 'PARKWAY', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ PKWY /', ' PARKWAY ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ BLVD$/', ' BOULEVARD', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ BLVD /', ' BOULEVARD ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/ BLVD/', ' BOULEVARD ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/^BCH /', 'BEACH ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/^E /', 'EAST ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/^W /', 'WEST ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/^N /', 'NORTH ', {column} );
    UPDATE {table} SET {column} = preg_replace( '/^S /', 'SOUTH ', {column} );
    '''.format(table=table, column=column)

def clean_boro(table, column, replacements):
    """ Retuns an SQL statement that cleans up borough columns.
        |replacements| is a dict mapping the cleaned borough codes (mn, bk, si, qn, br)
        to the unclean borough codes.
    """
    return '''
    UPDATE {table} SET {column} = preg_replace('/{mn}/i', 'MN', {column});
    UPDATE {table} SET {column} = preg_replace('/{bk}/i', 'BK', {column});
    UPDATE {table} SET {column} = preg_replace('/{si}/i', 'SI', {column});
    UPDATE {table} SET {column} = preg_replace('/{qn}/i', 'QN', {column});
    UPDATE {table} SET {column} = preg_replace('/{br}/i', 'BR', {column});
    '''.format(table=table, column=column, mn=replacements["mn"], bk=replacements["bk"],
            si=replacements["si"], qn=replacements["qn"], br=replacements["br"])
