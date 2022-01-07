'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { isValidHttpUrl } from './validation';

describe( 'helpers/validation', () => {
	describe( 'isValidHttpUrl', () => {
		it( 'should accept valid values', () => {
			const urls = [
				'https://example.org',
				'https://example.org/foo?bar=1&baz=2',
				'https://example.org/foo?bar=1;baz=2',
				'https://example.org/foo?bar=a+b+c+d',
				'https://example.org/foo?bar=a|b|c|d',
				'https://example.org/foo?bar=a:b:c:d',
				'https://example.org/foo?bar=a%20b%20c%20d',
				'https://example.org#fragement',
				'https://[2001:db8::1]:80',
				'https://[::1]',
				'https://127.0.0.1',
				'https://127.0.0.1:8080',
				'https://localhost',
				'https://ru.wikipedia.org/wiki/%D0%A3%D1%87%D0%B0%D1%81%D1%82%D0%BD%D0%B8%D0%BA:Serhio_Magpie/instantDiffs.js',
				'https://ru.wikipedia.org/wiki/Участник:Serhio_Magpie/instantDiffs.js',
				'https://🦄🎉.toolforge.org/',
				'http://xn--dk8hv9g.toolforge.org/'
			];

			urls.forEach( ( url ) => {
				expect( isValidHttpUrl( url ), url ).to.be.true;
			} );
		} );

		it( 'should reject invalid values', () => {
			const urls = [
				'example.org/',
				'ldap://example.org',
				'https://',
				'http://',
				'https://example.org/path with spaces',
				'http://example.org?q=Spaces should be encoded'
			];

			urls.forEach( ( url ) => {
				expect( isValidHttpUrl( url ), url ).to.be.false;
			} );
		} );

	} );
} );
