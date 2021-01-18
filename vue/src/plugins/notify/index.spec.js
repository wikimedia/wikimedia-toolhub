'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { setStore, methods, install } from './index';

let $store;

describe( 'notify/index', () => {
	beforeEach( () => {
		$store = { dispatch: sinon.spy() };
		setStore( $store );
	} );

	describe( 'methods', () => {
		it( 'success', () => {
			methods.success( 'success message' );

			expect( $store.dispatch ).to.have.been.calledOnce;
			expect( $store.dispatch ).to.have.been.calledWithExactly(
				'notify/success', { message: 'success message', timeout: 0 }
			);
		} );

		it( 'info', () => {
			methods.info( 'info message' );

			expect( $store.dispatch ).to.have.been.calledOnce;
			expect( $store.dispatch ).to.have.been.calledWithExactly(
				'notify/info', { message: 'info message', timeout: 0 }
			);
		} );

		it( 'warning', () => {
			methods.warning( 'warning message' );

			expect( $store.dispatch ).to.have.been.calledOnce;
			expect( $store.dispatch ).to.have.been.calledWithExactly(
				'notify/warning', 'warning message'
			);
		} );

		it( 'error', () => {
			methods.error( 'error message' );

			expect( $store.dispatch ).to.have.been.calledOnce;
			expect( $store.dispatch ).to.have.been.calledWithExactly(
				'notify/error', 'error message'
			);
		} );

		it( 'clear', () => {
			methods.clear( 31337 );

			expect( $store.dispatch ).to.have.been.calledOnce;
			expect( $store.dispatch ).to.have.been.calledWithExactly(
				'notify/clearMessage', 31337
			);
		} );
	} );

	describe( 'install', () => {
		it( 'happy path', () => {
			const vue = { component: sinon.spy(), prototype: sinon.spy() };
			const store = { registerModule: sinon.spy() };

			install( vue, { store: store } );

			expect( install.installed ).to.be.a( 'boolean' ).that.is.true;
			expect( store.registerModule ).to.have.been.calledOnce;
			expect( vue.component ).to.have.been.calledOnce;
			expect( vue.prototype.$notify ).to.be.an( 'object' );
		} );
	} );

} );
