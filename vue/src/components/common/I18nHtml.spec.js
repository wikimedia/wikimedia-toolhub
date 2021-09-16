/* eslint-disable no-unused-vars */
'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;

import { shallowMount } from '@vue/test-utils';

import I18nHtml from './I18nHtml';

describe( 'components/common', () => {
	describe( 'I18nHtml', () => {
		it( 'should render', () => {
			const wrapper = shallowMount(
				I18nHtml, {
					propsData: {
						msg: 'footer-content-license',
						tag: 'p'
					},
					slots: {
						default: [ ' ', '<a href="/test">test</a>', ' ' ]
					}
				}
			);

			expect( wrapper ).to.be.an( 'object' );
			expect( wrapper.element.tagName ).to.equal( 'P' );
			const links = wrapper.findAll( 'a' );
			expect( links.length ).to.equal( 1 );
			expect( links.at( 0 ).html() ).to.contain( 'test' );
		} );
	} );
} );
