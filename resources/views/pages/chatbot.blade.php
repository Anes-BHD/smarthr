@extends('layouts.app')
@section('page-content')
    <div class="content container-fluid">
        <!-- Page Header -->
        <x-breadcrumb>
            <x-slot name="title">{{ __('AI Assistant') }}</x-slot>
            <ul class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ route('dashboard') }}">{{ __('Dashboard') }}</a></li>
                <li class="breadcrumb-item active">{{ __('Chatbot') }}</li>
            </ul>
        </x-breadcrumb>
        <!-- /Page Header -->

        <div class="row">
            <div class="col-sm-12">
                <div class="card">
                    <div class="card-body text-center" style="padding: 100px 0;">
                        <i class="la la-comments" style="font-size: 4rem; color: #ccc;"></i>
                        <h3 class="mt-3">AI Assistant Coming Soon!</h3>
                        <p class="text-muted">Once integrated with an AI backend, you can chat with your SmartHR assistant right here.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection
