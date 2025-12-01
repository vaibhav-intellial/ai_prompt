import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .utils import read_file, compare_data
from .models import BOMComparison


# ------------------------------
# JSON SANITIZER (MAIN FIX)
# ------------------------------
def sanitize_json(obj):
    """Recursively convert objects into JSON-safe values."""
    try:
        if isinstance(obj, dict):
            return {k: sanitize_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_json(i) for i in obj]
        elif pd.isna(obj):
            return None
        elif isinstance(obj, float):
            if obj in [float("inf"), float("-inf")]:
                return None
            return float(obj)
        elif isinstance(obj, (int, str, bool)) or obj is None:
            return obj
        else:
            # Convert numpy types, tuples, datetime, etc.
            return str(obj)
    except Exception:
        return None


# ------------------------------
# Helper for sanitizing pandas DF
# ------------------------------
def sanitize_df(df):
    """Convert NaN/NaT/inf into None."""
    df = df.where(pd.notnull(df), None)
    df = df.replace([float("inf"), float("-inf")], None)
    return df


# ------------------------------
# MAIN VIEW
# ------------------------------
def compare_boms(request):
    """Handles file upload, comparison, and saving JSON to database."""
    try:
        if request.method == 'POST':

            master_file = request.FILES.get('master_file')
            user_file = request.FILES.get('user_file')

            if not master_file or not user_file:
                comparisons = BOMComparison.objects.all().order_by('-created_at')
                return render(request, 'core/index.html', {
                    'error': 'Please upload both files.',
                    'comparisons': comparisons
                })

            # Read uploaded files
            master_data_df = read_file(master_file)
            user_data_df = read_file(user_file)

            # Compare data
            comparison_result_dict = compare_data(master_data_df, user_data_df)

            # 🔥 Sanitize dataframes
            master_data_df = sanitize_df(master_data_df)
            user_data_df = sanitize_df(user_data_df)

            master_data_for_db = master_data_df.to_dict('records')
            user_data_for_db = user_data_df.to_dict('records')

            # 🔥 MOST IMPORTANT FIX → sanitize comparison_result
            comparison_result_for_db = sanitize_json(comparison_result_dict)

            # Save to DB
            new_comparison = BOMComparison.objects.create(
                master_filename=master_file.name,
                user_filename=user_file.name,
                master_data=master_data_for_db,
                user_data=user_data_for_db,
                comparison_result=comparison_result_for_db
            )

            return redirect('core:comparison_result', pk=new_comparison.id)

        # GET → list old comparisons
        comparisons = BOMComparison.objects.all().order_by('-created_at')
        return render(request, 'core/index.html', {'comparisons': comparisons})

    except Exception as e:
        print("🐍 compare_boms error:", e)
        comparisons = BOMComparison.objects.all().order_by('-created_at')
        return render(request, 'core/index.html', {
            'error': f'An error occurred: {e}',
            'comparisons': comparisons
        })


# ------------------------------
# RESULT PAGE
# ------------------------------
def comparison_result(request, pk):
    try:
        comparison_obj = get_object_or_404(BOMComparison, pk=pk)

        master_data_raw = comparison_obj.master_data
        user_data_raw = comparison_obj.user_data
        comparison_result_dict = comparison_obj.comparison_result

        master_filename = comparison_obj.master_filename
        user_filename = comparison_obj.user_filename

        user_bom_for_display = []

        # Unchanged
        for row in comparison_result_dict.get('unchanged', []):
            item = row.copy()
            item['row_status'] = 'unchanged'
            user_bom_for_display.append(item)

        # Modified
        for row in comparison_result_dict.get('modified', []):
            item = row['user'].copy()
            item['MPN'] = row['MPN']
            item['row_status'] = 'modified'
            item['master_version_data'] = row['master'].copy()
            user_bom_for_display.append(item)

        # Added
        for row in comparison_result_dict.get('added', []):
            item = row.copy()
            item['row_status'] = 'added'
            user_bom_for_display.append(item)

        # Sort by MPN
        if user_bom_for_display and 'MPN' in user_bom_for_display[0]:
            user_bom_for_display.sort(key=lambda x: x.get('MPN', ''))
        context = {
            'master_data_raw': master_data_raw,
            'user_data_raw': user_data_raw,
            'comparison_result': comparison_result_dict,
            'user_bom_for_display': user_bom_for_display,
            'master_filename': master_filename,
            'user_filename': user_filename,
            'comparison_id': pk
        }
        return render(request, 'core/result.html', context)

    except Exception as e:
        print("🐍 comparison_result error:", e)
        comparisons = BOMComparison.objects.all().order_by('-created_at')
        return render(request, 'core/index.html', {
            'error': f'An error occurred: {e}',
            'comparisons': comparisons
        })


# ------------------------------
# DOWNLOAD JSON
# ------------------------------
def download_comparison_json(request, pk):
    try:
        comparison_obj = get_object_or_404(BOMComparison, pk=pk)
        comparison_result_dict = comparison_obj.comparison_result

        if comparison_result_dict:
            response = JsonResponse(comparison_result_dict, safe=False)
            response['Content-Disposition'] = (
                f'attachment; filename="bom_comparison_result_{pk}.json"'
            )
            return response

        return JsonResponse({'error': 'No comparison result found.'}, status=404)

    except Exception as e:
        print("🐍 download_json error:", e)
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)
