'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import {
	DEFAULT_LOCALE,
	LOCALE_KEY,
	sanitizeLocale,
	initialLocale,
	actions,
	mutations
} from './locale';

describe( 'store/locale', () => {
	describe( 'sanitizeLocale', () => {
		it( 'should return DEFAULT_LOCALE if given garbage', () => {
			expect( sanitizeLocale( undefined ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( null ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( false ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( true ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( {} ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( [] ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( '' ) ).to.equal( DEFAULT_LOCALE );
			expect( sanitizeLocale( 'xyzzy' ) ).to.equal( DEFAULT_LOCALE );
		} );

		it( 'should convert BCP47 codes', () => {
			expect( sanitizeLocale( 'en-US' ) ).to.equal( 'en' );
			expect( sanitizeLocale( 'en-GB' ) ).to.equal( 'en-gb' );
			expect( sanitizeLocale( 'en-CA' ) ).to.equal( 'en-ca' );
			expect( sanitizeLocale( 'en-SimPle' ) ).to.equal( 'en-simple' );
		} );

		it( 'should resolve aliases', () => {
			expect( sanitizeLocale( 'zh-classical' ) ).to.equal( 'lzh' );
			expect( sanitizeLocale( 'bbc' ) ).to.equal( 'bbc-latn' );
			expect( sanitizeLocale( 'cbk-zam' ) ).to.equal( 'cbk' );
		} );
	} );

	describe( 'actions', () => {
		const stubVm = {
			$i18n: { locale: null, formatter: null },
			$route: { query: sinon.stub() },
			$router: { push: sinon.stub() },
			$vuetify: { rtl: null },
			$moment: { locale: sinon.stub() }
		};

		beforeEach( () => {
			sinon.reset();
		} );

		it( 'initializeLocale', () => {
			const commit = sinon.spy();
			const dispatch = sinon.spy();
			const state = {};

			actions.initializeLocale(
				{ commit, dispatch, state },
				{ vm: stubVm }
			);

			expect( commit ).to.not.have.been.called;

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'setLocale',
				{ vm: stubVm, initial: true, locale: initialLocale }
			);
		} );

		it( 'initializeLocale with ?uselang=qqx', () => {
			const commit = sinon.spy();
			const dispatch = sinon.spy();
			const state = {};
			stubVm.$route.query = { uselang: 'qqx' };

			actions.initializeLocale(
				{ commit, dispatch, state },
				{ vm: stubVm }
			);

			expect( commit ).to.not.have.been.called;

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'setLocale',
				{ vm: stubVm, initial: true, locale: 'qqx' }
			);
		} );

		it( 'setLocale', () => {
			const commit = sinon.spy();
			const dispatch = sinon.stub();
			const state = {};
			const rootState = { api: { schemaPromise: null } };

			dispatch.onFirstCall().returns( { then: sinon.stub().yields() } );
			const testLocale = 'en';

			actions.setLocale(
				{ commit, dispatch, state, rootState },
				{ locale: testLocale, vm: stubVm }
			);

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledBefore( commit );
			expect( dispatch ).to.have.been.calledWithExactly(
				'user/setLocale', testLocale, { root: true }
			);

			expect( commit ).to.have.been.calledOnce;
			expect( commit ).to.have.been.calledWithExactly(
				'onLocaleChanged', { locale: testLocale }
			);

			expect( stubVm.$i18n.locale ).to.equal( testLocale );
			expect( stubVm.$i18n.formatter ).to.be.an( 'object' );
			expect( stubVm.$vuetify.rtl ).to.equal( false );

			expect( stubVm.$moment.locale ).to.have.been.calledOnce;
			expect( stubVm.$moment.locale ).to.have.been.calledWithExactly(
				testLocale
			);

			expect( stubVm.$router.push ).to.have.been.calledOnce;
			expect( stubVm.$router.push ).to.have.been.calledWithExactly(
				{ query: { uselang: testLocale } }
			);
		} );

		it( 'setLocale initial: true', () => {
			const commit = sinon.spy();
			const dispatch = sinon.stub();
			const state = {};
			const rootState = { api: { schemaPromise: null } };

			dispatch.onFirstCall().returns( { then: sinon.stub().yields() } );
			const testLocale = 'ar';

			actions.setLocale(
				{ commit, dispatch, state, rootState },
				{ locale: testLocale, vm: stubVm, initial: true }
			);

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledBefore( commit );
			expect( dispatch ).to.have.been.calledWithExactly(
				'user/setLocale', testLocale, { root: true }
			);

			expect( commit ).to.have.been.calledOnce;
			expect( commit ).to.have.been.calledWithExactly(
				'onLocaleChanged', { locale: testLocale }
			);

			expect( stubVm.$i18n.locale ).to.equal( testLocale );
			expect( stubVm.$i18n.formatter ).to.be.an( 'object' );
			expect( stubVm.$vuetify.rtl ).to.equal( true );

			expect( stubVm.$moment.locale ).to.have.been.calledOnce;
			expect( stubVm.$moment.locale ).to.have.been.calledWithExactly(
				testLocale
			);

			expect( stubVm.$router.push ).to.not.have.been.called;
		} );
	} );

	describe( 'mutations', () => {
		it( 'onLocaleChanged', () => {
			const state = { locale: null };
			const storage = sinon.spy(
				// eslint-disable-next-line no-proto
				window.localStorage.__proto__, 'setItem'
			);

			const locale = 'whatever';
			mutations.onLocaleChanged( state, { locale: locale } );

			expect( storage ).to.have.been.calledWith( LOCALE_KEY, locale );
			expect( state.locale ).to.equal( locale );
		} );
	} );

} );
