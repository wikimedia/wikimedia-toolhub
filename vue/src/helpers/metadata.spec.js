'use strict';
import chai from 'chai';

const expect = chai.expect;

import { fetchMetaInfo } from './metadata';

describe( 'helpers/metadata', () => {
	describe( 'fetchMetaInfo', () => {
		const pagekeys = [
			{
				pagekey: 'lists',
				suffix: 'view'
			},
			{
				pagekey: 'addremovetools',
				suffix: false
			}
		];

		pagekeys.forEach( ( { pagekey, suffix } ) => {
			it( `should return structured data for ${pagekey}`, () => {
				const metadata = fetchMetaInfo( pagekey, suffix );
				expect( metadata ).to.be.an( 'object' );
				expect( metadata ).to.have.a.property( 'title' );
				expect( metadata ).to.have.a.property( 'meta' );
				expect( metadata.meta ).to.be.an( 'array' ).of.length( 4 );
				expect( metadata.meta[ 0 ] ).to.be.an( 'object' );
				expect( metadata.meta[ 0 ] ).to.have.a.property( 'property' );
				expect( metadata.meta[ 0 ] ).to.have.a.property( 'content' );
				expect( metadata.meta[ 1 ] ).to.be.an( 'object' );
				expect( metadata.meta[ 1 ] ).to.have.a.property( 'name' );
				expect( metadata.meta[ 1 ] ).to.have.a.property( 'content' );
				expect( metadata.meta[ 2 ] ).to.be.an( 'object' );
				expect( metadata.meta[ 2 ] ).to.have.a.property( 'name' );
				expect( metadata.meta[ 2 ] ).to.have.a.property( 'content' );
				expect( metadata.meta[ 3 ] ).to.be.an( 'object' );
				expect( metadata.meta[ 3 ] ).to.have.a.property( 'property' );
				expect( metadata.meta[ 3 ] ).to.have.a.property( 'content' );
			} );
		} );
	} );
} );
