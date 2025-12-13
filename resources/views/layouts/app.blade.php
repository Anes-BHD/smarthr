@extends('layouts.blank')

@section('content')
    <!-- Header -->
    @include('partials.header')
    <!-- /Header -->
    <!-- Sidebar -->
    @hasSection('sidebar')
        @yield('sidebar')
    @else
        @include('partials.sidebar')
    @endif
    <!-- /Sidebar -->
    <!-- Page Wrapper -->
    <div class="page-wrapper">
        <div id="loader-wrapper">
            <div id="loader">
              <div class="loader-ellips">
                <span class="loader-ellips__dot"></span>
                <span class="loader-ellips__dot"></span>
                <span class="loader-ellips__dot"></span>
                <span class="loader-ellips__dot"></span>
              </div>
            </div>
        </div>
        <script>
            // Fallback to hide loader if main JavaScript fails
            (function() {
                function hideLoader() {
                    var loader = document.getElementById('loader-wrapper');
                    if (loader) {
                        loader.style.display = 'none';
                    }
                }
                // Try to hide after page loads
                if (document.readyState === 'complete') {
                    setTimeout(hideLoader, 600);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(hideLoader, 600);
                    });
                }
                // Also hide after DOM is ready (jQuery fallback)
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(hideLoader, 600);
                    });
                }
            })();
        </script>
        <!-- Page Content -->
        @yield('page-content')
        <!-- /Page Content -->
    </div>
    <!-- /Page Wrapper -->
    <!-- Delete Modal -->
    <div class="modal custom-modal fade" id="GeneralDeleteModal" role="dialog">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body">
                    <div class="form-header">
                        <h3 class="modal_title">Delete</h3>
                        <p class="modal_message">Are you sure want to delete?</p>
                    </div>
                    <form method="post">
                        @method('DELETE')
                        @csrf
                        <div class="modal-btn delete-action">
                            <input type="hidden" name="id">
                            <div class="row">
                                <div class="col-6">
                                    <a href="javascript:void(0);" data-bs-dismiss="modal"
                                        class="btn btn-primary cancel-btn">{{ __('Cancel') }}</a>
                                </div>
                                <div class="col-6">
                                    <button type="submit"
                                        class="btn btn-primary continue-btn w-100">{{ __('Delete') }}</button>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <!-- /Delete Modal -->

@endsection
