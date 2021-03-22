'use strict';
import chai from 'chai';

const expect = chai.expect;

import { forWikiLabel } from './tools';

describe( 'tools', () => {
	describe( 'forWikiLabel', () => {
		it( 'should transform special values', () => {
			expect( forWikiLabel( '*' ) ).to.equal( 'Any wiki' );
			expect( forWikiLabel( 'commons.wikimedia.org' ) ).to.equal( 'Wikimedia Commons' );
			expect( forWikiLabel( 'mediawiki.org' ) ).to.equal( 'MediaWiki wiki' );
			expect( forWikiLabel( 'www.mediawiki.org' ) ).to.equal( 'MediaWiki wiki' );
			expect( forWikiLabel( '*.mediawiki.org' ) ).to.equal( 'MediaWiki wiki' );
		} );
		it( 'should pass through unknown values', () => {
			expect( forWikiLabel( 'pizza' ) ).to.equal( 'pizza' );
		} );
	} );
} );
