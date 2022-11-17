'use strict';
import chai from 'chai';

const expect = chai.expect;

import { forWikiLabel, localizeEnum } from './tools';

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
	describe( 'localizeEnum', () => {
		it( 'should localize known values', () => {
			expect( localizeEnum( 'audiences', 'admin' ) ).to.equal( 'Admins' );
			expect( localizeEnum( 'content_types', 'data::event' ) ).to.equal( 'Event data' );
		} );
		it( 'should mangle unknown values', () => {
			expect( localizeEnum( 'foo_bar', 'baz xyzzy::plugh_plover' ) ).to.equal( 'search-filter-foo-bar-baz-xyzzy-plugh-plover' );
		} );
		it( 'should handle null values gracefully', () => {
			expect( localizeEnum( 'tool_type', null ) ).to.equal( '' );
		} );
	} );
} );
