'use strict';
import chai from 'chai';
import sinon from 'sinon';
import * as swagger from '@/plugins/swagger';
import i18n from '@/plugins/i18n';
chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-underscore-dangle */
/* eslint-disable no-unused-expressions */

import { displayErrorNotification } from './notifications';

describe( 'helpers/notifications', () => {

	const data = {
		failure: {
			errors: [
				{ field: 'test field1', message: 'something went wrong' },
				{ field: 'test field2', message: 'something went wrong' }
			]
		}
	};

	const stubThis = {
		_vm: {
			$notify: {
				error: sinon.stub()
			}

		}
	};

	let t = 'func';
	let getFailurePayload = 'func';

	beforeEach( () => {
		t = sinon.stub( i18n, 't' );
		getFailurePayload = sinon.stub( swagger, 'getFailurePayload' ).callsFake( ( param ) => param );
	} );

	afterEach( () => {
		t.restore();
		getFailurePayload.restore();
		sinon.reset();
	} );

	describe( 'displayErrorNotification', () => {
		it( 'should call this._vm.$notify.error', () => {
			displayErrorNotification.call( stubThis, data.failure );
			expect( getFailurePayload ).to.have.been.calledOnce;
			expect( t ).to.have.been.calledTwice;
			expect( stubThis._vm.$notify.error ).to.have.been.calledTwice;
		} );
	} );
} );
