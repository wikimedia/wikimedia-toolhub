'use strict';
import chai from 'chai';

const expect = chai.expect;

import { makeURLQueryParams } from './swagger';

describe( 'plugins/swagger', () => {

	describe( 'makeURLQueryParams', () => {
		it( 'should return properly formatted URLSearchParams object', () => {
			const input = [
				[ 'page', 1 ],
				[ 'username__contains', 'raymond' ],
				[ 'groups__id', 4 ],
				[ 'ordering', '-username' ]
			];
			const output = 'page=1&username__contains=raymond&groups__id=4&ordering=-username';

			expect( makeURLQueryParams( input ).toString() ).to.equal( output );
		} );

		it( 'should remove params with undefined or null values', () => {
			const input = [
				[ 'page', 1 ],
				[ 'username__contains', undefined ],
				[ 'groups__id', null ],
				[ 'ordering', '-username' ]
			];
			const output = 'page=1&ordering=-username';

			expect( makeURLQueryParams( input ).toString() ).to.equal( output );
		} );
	} );
} );
